import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading
import logging
from datetime import datetime

# 生成带有时间戳的日志文件名
log_filename = datetime.now().strftime('socket_http_keepalive_%Y%m%d-%H%M%S.log')

# 配置日志记录
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==============================
# 方案一：使用 requests.Session (自动Keep-Alive)
# ==============================
def http_keepalive_session(url, requests_count=5):
    """
    使用 requests.Session 自动管理长连接
    注意：需要服务端支持 Keep-Alive
    """
    with requests.Session() as s:
        # 配置重试策略（可选）
        retries = Retry(total=3,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])

        # 挂载适配器
        s.mount('http://', HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=100))
        s.mount('https://', HTTPAdapter(max_retries=retries))

        for i in range(requests_count):
            try:
                response = s.get(url, timeout=(3.05, 30))  # (连接超时, 读取超时)

                # 打印连接复用信息
                print(f"请求 [{i + 1}] 响应状态: {response.status_code}")
                print(f"使用连接: {response.raw.connection}")
                print(f"响应头 Connection: {response.headers.get('Connection')}\n")

            except requests.exceptions.RequestException as e:
                print(f"请求失败: {str(e)}")
                break


# ==============================
# 方案二：底层 socket 实现 (手动管理)
# ==============================
import socket
import time


def raw_socket_keepalive(url, port=80, requests_count=300):
    """
    使用原始 socket 手动管理长连接
    适用于需要精细控制场景
    """
    # 解析目标地址
    host = url.split("//")[-1].split("/")[0]
    path = '/' + '/'.join(url.split("//")[-1].split("/")[1:])

    # 创建 TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)  # 设置超时

    try:
        # 建立连接
        sock.connect((host, port))
        logging.info(f"已连接到 {host}:{port} (使用 HTTPS)")

        for i in range(requests_count):
            # 构建 HTTP 请求
            request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                "Connection: keep-alive\r\n"  # 关键头
                "User-Agent: PythonKeepAlive/1.0\r\n"
                "\r\n"
            ).encode('utf-8')

            # 发送请求
            sock.sendall(request)
            logging.info(f"已发送请求 [{i + 1}]")

            # 接收响应
            response = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                # 简单判断响应结束（实际应解析 Content-Length 或 Transfer-Encoding）
                if b"\r\n\r\n" in response and len(chunk) < 4096:
                    break

            # 打印响应头
            headers = response.split(b"\r\n\r\n")[0].decode()
            content = response.split(b"\r\n\r\n")[1].decode()

            logging.info(f"响应 [{i + 1}] 头信息:\n{headers}\n")
            logging.info(f"响应 [{i + 1}] 内容:\n{content}\n")

            # 模拟间隔
            time.sleep(1)

    except socket.error as e:
        logging.error(f"Socket错误: {str(e)}")
        print(f"Socket错误: {str(e)}")
    finally:
        sock.close()
        logging.info("连接已关闭")

# 多线程执行
def run_threads(target_url, port, thread_count, requests_count):
    threads = []
    for _ in range(thread_count):
        thread = threading.Thread(target=raw_socket_keepalive, args=(target_url, port, requests_count))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


# ==============================
# 测试执行
# ==============================
if __name__ == "__main__":
    target_url = "http://pa-nlb-876b517a8941d030.elb.ap-east-1.amazonaws.com/"

    # print("=" * 50)
    # print("测试方案一：requests.Session")
    # http_keepalive_session(target_url)

    #print("\n" + "=" * 50)
    #print("测试方案二：原始 socket 实现")
    #raw_socket_keepalive(target_url, port=80)

    thread_count = 100  # 线程数量
    requests_count = 300  # 每个线程的请求数量

    print("\n" + "=" * 50)
    print("测试方案二：原始 socket 实现")
    run_threads(target_url, port=80, thread_count=thread_count, requests_count=requests_count)
