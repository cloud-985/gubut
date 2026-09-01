"""SSH 隧道工具类：通过代理 127.0.0.1:18080 连接远程服务器 111.91.30.57"""
import paramiko
import os

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASS = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080
REMOTE_BASE = "/www/wwwroot/gubut"


def _get_transport():
    """建立通过 HTTP CONNECT 代理的 SSH Transport"""
    sock = __import__("socket").socket(__import__("socket").AF_INET, __import__("socket").SOCK_STREAM)
    sock.connect((PROXY_HOST, PROXY_PORT))
    # HTTP CONNECT
    sock.sendall(f"CONNECT {HOST}:{PORT} HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n\r\n".encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = sock.recv(4096)
        if not chunk:
            break
        resp += chunk
    if b"200" not in resp.split(b"\r\n")[0]:
        raise RuntimeError(f"Proxy CONNECT failed: {resp[:200]}")
    transport = paramiko.Transport(sock)
    transport.start_client()
    transport.auth_password(USER, PASS)
    return transport


def run_remote(cmd, timeout=30):
    """执行远程 shell 命令并返回 stdout 字符串"""
    transport = _get_transport()
    try:
        channel = transport.open_session()
        channel.settimeout(timeout)
        channel.exec_command(cmd)
        out = b""
        while True:
            chunk = channel.recv(4096)
            if not chunk:
                break
            out += chunk
        # 等命令结束
        channel.recv_exit_status()
        return out.decode("utf-8", errors="replace")
    finally:
        transport.close()


def read_remote_file(path):
    """读取远程文件内容为字符串"""
    return run_remote(f"cat {path}")


def write_remote_file(path, content):
    """用 base64 编码写入远程文件（安全传输中文/二进制）"""
    import base64
    b64 = base64.b64encode(content.encode("utf-8")).decode()
    run_remote(f"echo {b64} | base64 -d > {path}")


def upload_local_to_remote(local_path, remote_path):
    """通过 SFTP（经代理）上传本地文件"""
    transport = _get_transport()
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        transport.close()


def list_remote_dir(path):
    """列出远程目录"""
    transport = _get_transport()
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        files = sftp.listdir(path)
        sftp.close()
        return files
    finally:
        transport.close()


if __name__ == "__main__":
    print("Testing connection...")
    out = run_remote(f"ls -la {REMOTE_BASE}")
    print(out[:500])
