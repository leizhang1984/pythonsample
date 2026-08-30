import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from azure.core.exceptions import AzureError, ResourceNotFoundError
from azure.identity import ClientSecretCredential
from azure.keyvault.certificates import CertificateClient
from cryptography import x509
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import pkcs12


# ============================================================
# Configuration
# ============================================================

TENANT_ID = os.environ["AZURE_TENANT_ID"]
CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]

PFX_PASSWORD = os.environ.get("PFX_PASSWORD", "")

KEY_VAULT_NAME = "leikeyvault01"
CERTIFICATE_NAME = "cert01"

#需要监控的本地文件夹路径，需要包含至少一个pfx证书文件，程序会自动扫描该文件夹下的所有pfx证书文件，并选择最新的证书上传到Azure Key Vault中
WATCH_FOLDER = Path(r"D:\Work\GitHub\pythonsample\azuremanagement\keyvault\cerfiticate")

EXPECTED_SAN_NAMES = { "*.leizhang.com", }

SCAN_INTERVAL_SECONDS = 30
FILE_STABILITY_SECONDS = 3


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


@dataclass(frozen=True)
class LocalCertificate:
    path: Path
    pfx_bytes: bytes
    thumbprint: str
    san_names: frozenset[str]
    not_before: datetime
    not_after: datetime


@dataclass(frozen=True)
class RemoteCertificate:
    thumbprint: str | None
    not_before: datetime | None
    not_after: datetime | None
    version: str | None


# ============================================================
# Azure client
# ============================================================

def create_certificate_client() -> CertificateClient:
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    return CertificateClient(
        vault_url=(
            f"https://{KEY_VAULT_NAME}.vault.azure.net"
        ),
        credential=credential,
    )


# ============================================================
# Utility functions
# ============================================================

def to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def normalize_dns_name(name: str) -> str:
    return name.strip().lower().rstrip(".")


def get_stable_pfx_files() -> list[Path]:
    """
    Return all PFX files that remain unchanged during the
    stability interval.

    All files are checked using one shared wait period.
    """
    files = [
        path
        for path in WATCH_FOLDER.glob("*.pfx")
        if path.is_file()
    ]

    if not files:
        return []

    initial_states: dict[Path, tuple[int, int]] = {}

    for path in files:
        try:
            stat = path.stat()
            initial_states[path] = (
                stat.st_size,
                stat.st_mtime_ns,
            )
        except OSError as error:
            logging.error(
                "Unable to inspect %s: %s",
                path.name,
                error,
            )

    time.sleep(FILE_STABILITY_SECONDS)

    stable_files: list[Path] = []

    for path, initial_state in initial_states.items():
        try:
            stat = path.stat()
            current_state = (
                stat.st_size,
                stat.st_mtime_ns,
            )
        except FileNotFoundError:
            logging.warning(
                "File disappeared during scan: %s",
                path.name,
            )
            continue
        except OSError as error:
            logging.error(
                "Unable to inspect %s: %s",
                path.name,
                error,
            )
            continue

        if initial_state[0] == 0:
            logging.warning(
                "Skipping empty PFX file: %s",
                path.name,
            )
            continue

        if current_state != initial_state:
            logging.info(
                "File is still being copied; retrying later: %s",
                path.name,
            )
            continue

        stable_files.append(path)

    return stable_files


# ============================================================
# Certificate validation
# ============================================================

def validate_certificate_san(
    certificate: x509.Certificate,
) -> frozenset[str]:
    try:
        extension = (
            certificate.extensions.get_extension_for_class(
                x509.SubjectAlternativeName
            )
        )
    except x509.ExtensionNotFound as error:
        raise ValueError(
            "Certificate does not contain a SAN extension."
        ) from error

    actual_names = frozenset(
        normalize_dns_name(name)
        for name in extension.value.get_values_for_type(
            x509.DNSName
        )
    )

    expected_names = frozenset(
        normalize_dns_name(name)
        for name in EXPECTED_SAN_NAMES
    )

    if actual_names != expected_names:
        raise ValueError(
            "SAN mismatch. "
            f"Expected={sorted(expected_names)}, "
            f"actual={sorted(actual_names)}"
        )

    return actual_names


def read_local_certificate(
    path: Path,
) -> LocalCertificate:
    pfx_bytes = path.read_bytes()

    password = (
        PFX_PASSWORD.encode("utf-8")
        if PFX_PASSWORD
        else None
    )

    try:
        private_key, certificate, _ = (
            pkcs12.load_key_and_certificates(
                pfx_bytes,
                password,
            )
        )
    except ValueError as error:
        raise ValueError(
            "Unable to open PFX. Verify its password "
            "and file integrity."
        ) from error
    except UnsupportedAlgorithm as error:
        raise ValueError(
            "The PFX uses an unsupported encryption "
            "or certificate algorithm."
        ) from error

    if certificate is None:
        raise ValueError(
            "The PFX does not contain a certificate."
        )

    if private_key is None:
        raise ValueError(
            "The PFX does not contain a private key."
        )

    san_names = validate_certificate_san(certificate)

    not_before = to_utc(
        certificate.not_valid_before_utc
    )
    not_after = to_utc(
        certificate.not_valid_after_utc
    )

    now = datetime.now(timezone.utc)

    if not_after <= now:
        raise ValueError(
            f"Certificate expired at "
            f"{not_after.isoformat()}."
        )

    if not_before > now:
        raise ValueError(
            f"Certificate is not valid until "
            f"{not_before.isoformat()}."
        )

    return LocalCertificate(
        path=path,
        pfx_bytes=pfx_bytes,
        thumbprint=certificate.fingerprint(
            hashes.SHA1()
        ).hex().lower(),
        san_names=san_names,
        not_before=not_before,
        not_after=not_after,
    )


def collect_valid_certificates(
    paths: list[Path],
) -> list[LocalCertificate]:
    """
    Validate each PFX independently.

    A failed certificate is logged and ignored. Processing
    continues with all remaining files.
    """
    valid_certificates: list[LocalCertificate] = []

    for path in paths:
        try:
            certificate = read_local_certificate(path)

            logging.info(
                "PFX validation passed: file=%s, SAN=%s, "
                "expiration=%s",
                path.name,
                sorted(certificate.san_names),
                certificate.not_after.isoformat(),
            )

            valid_certificates.append(certificate)

        except (OSError, ValueError) as error:
            logging.error(
                "PFX rejected: file=%s, reason=%s",
                path.name,
                error,
            )

    return valid_certificates


def select_best_certificate(
    certificates: list[LocalCertificate],
) -> LocalCertificate | None:
    """
    Select the valid certificate with the latest expiration.

    If expiration dates are identical, select the one with the
    latest activation date.
    """
    if not certificates:
        return None

    return max(
        certificates,
        key=lambda certificate: (
            certificate.not_after,
            certificate.not_before,
            certificate.path.stat().st_mtime_ns,
        ),
    )


# ============================================================
# Key Vault operations
# ============================================================

def get_remote_certificate(
    client: CertificateClient,
) -> RemoteCertificate | None:
    try:
        certificate = client.get_certificate(
            CERTIFICATE_NAME
        )
    except ResourceNotFoundError:
        return None

    properties = certificate.properties

    return RemoteCertificate(
        thumbprint=(
            properties.x509_thumbprint.hex().lower()
            if properties.x509_thumbprint
            else None
        ),
        not_before=(
            to_utc(properties.not_before)
            if properties.not_before
            else None
        ),
        not_after=(
            to_utc(properties.expires_on)
            if properties.expires_on
            else None
        ),
        version=properties.version,
    )


def local_certificate_is_newer(
    local: LocalCertificate,
    remote: RemoteCertificate,
) -> bool:
    if remote.not_after is None:
        return True

    if local.not_after > remote.not_after:
        return True

    if (
        local.not_after == remote.not_after
        and remote.not_before is not None
        and local.not_before > remote.not_before
    ):
        return True

    return False


def import_certificate(
    client: CertificateClient,
    certificate: LocalCertificate,
) -> None:
    result = client.import_certificate(
        certificate_name=CERTIFICATE_NAME,
        certificate_bytes=certificate.pfx_bytes,
        password=PFX_PASSWORD or None,
        tags={
            "source": "local-certificate-sync",
            "source-file": certificate.path.name,
            "validated-san": ",".join(
                sorted(certificate.san_names)
            ),
        },
    )

    logging.info(
        "Certificate imported successfully. "
        "Certificate=%s, version=%s, expiration=%s",
        CERTIFICATE_NAME,
        result.properties.version,
        certificate.not_after.isoformat(),
    )


# ============================================================
# Synchronization
# ============================================================

def synchronize_best_certificate(
    client: CertificateClient,
) -> None:
    stable_files = get_stable_pfx_files()

    if not stable_files:
        logging.info(
            "No stable PFX files found in %s",
            WATCH_FOLDER,
        )
        return

    logging.info(
        "Found %d stable PFX file(s).",
        len(stable_files),
    )

    valid_certificates = collect_valid_certificates(
        stable_files
    )

    if not valid_certificates:
        logging.warning(
            "No valid PFX certificates passed validation."
        )
        return

    selected = select_best_certificate(
        valid_certificates
    )

    if selected is None:
        return

    logging.info(
        "Selected certificate: file=%s, "
        "expiration=%s, thumbprint=%s",
        selected.path.name,
        selected.not_after.isoformat(),
        selected.thumbprint,
    )

    remote = get_remote_certificate(client)

    if remote is None:
        logging.info(
            "Certificate %s does not exist in Key Vault.",
            CERTIFICATE_NAME,
        )
        import_certificate(client, selected)
        return

    if selected.thumbprint == remote.thumbprint:
        logging.info(
            "The selected certificate already exists as "
            "the latest Key Vault version; skipping."
        )
        return

    if not local_certificate_is_newer(
        selected,
        remote,
    ):
        logging.warning(
            "Selected local certificate is not newer; "
            "skipping. Local expiration=%s, "
            "Key Vault expiration=%s",
            selected.not_after.isoformat(),
            (
                remote.not_after.isoformat()
                if remote.not_after
                else "unknown"
            ),
        )
        return

    logging.info(
        "Selected certificate is newer than Key Vault "
        "version %s; importing a new version.",
        remote.version,
    )

    import_certificate(client, selected)


# ============================================================
# Main loop
# ============================================================

def main() -> None:
    WATCH_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    client = create_certificate_client()

    logging.info(
        "Monitoring folder=%s, Key Vault=%s, "
        "certificate=%s, expected SAN=%s",
        WATCH_FOLDER,
        KEY_VAULT_NAME,
        CERTIFICATE_NAME,
        sorted(EXPECTED_SAN_NAMES),
    )

    while True:
        try:
            synchronize_best_certificate(client)

        except AzureError:
            logging.exception(
                "Azure Key Vault operation failed."
            )
        except OSError:
            logging.exception(
                "Unable to scan the certificate folder."
            )

        time.sleep(SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info(
            "Certificate synchronization stopped by user."
        )
