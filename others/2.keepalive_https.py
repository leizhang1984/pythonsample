import socket
import ssl
import time
import threading
import logging
from datetime import datetime

# 生成带有时间戳的日志文件名
log_filename = datetime.now().strftime('socket_keepalive_%Y%m%d-%H%M%S.log')

# 配置日志记录
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def raw_socket_keepalive(url, port=443, requests_count=300):
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

    # 创建 SSL 上下文
    context = ssl.create_default_context()
    #context.load_verify_locations("D:\Work\Doc\FYNow\Customer\TPLink\gwlb.leiweb.net\certificate.crt")

    try:
        # 建立连接并进行 SSL/TLS 握手
        wrapped_sock = context.wrap_socket(sock, server_hostname=host)
        wrapped_sock.connect((host, port))
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
            wrapped_sock.sendall(request)
            logging.info(f"已发送请求 [{i + 1}]")

            # 接收响应
            response = b''
            while True:
                chunk = wrapped_sock.recv(4096)
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
        wrapped_sock.close()
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
    target_url = "https://gwlb.leiweb.net"
    
    # print("\n" + "=" * 50)
    # print("测试方案二：原始 socket 实现")
    # raw_socket_keepalive(target_url, port=443)

    thread_count = 30  # 线程数量
    requests_count = 600  # 每个线程的请求数量

    print("\n" + "=" * 50)
    print("测试方案二：原始 socket 实现")
    run_threads(target_url, port=443, thread_count=thread_count, requests_count=requests_count)