"""
SSH隧道模块 - 通过HTTP CONNECT代理连接远程服务器
"""
import paramiko
import json
import io
import socket

# 远程服务器配置
SSH_HOST = "111.91.30.57"
SSH_PORT = 22
SSH_USER = "root"
SSH_PASS = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080
REMOTE_DIR = "/www/wwwroot/gubut"


def _http_connect_tunnel():
    """通过HTTP CONNECT方法建立到SSH服务器的隧道socket"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((PROXY_HOST, PROXY_PORT))

    # 发送HTTP CONNECT请求
    target = f"{SSH_HOST}:{SSH_PORT}"
    connect_req = (
        f"CONNECT {target} HTTP/1.1\r\n"
        f"Host: {target}\r\n"
        f"Proxy-Connection: keep-alive\r\n"
        f"\r\n"
    )
    sock.sendall(connect_req.encode("utf-8"))

    # 读取响应（直到双CRLF）
    response = b""
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            sock.close()
            raise ConnectionError("HTTP CONNECT proxy closed connection before response")
        response += chunk
        if len(response) > 16384:
            sock.close()
            raise ConnectionError("HTTP CONNECT proxy response too large")

    # 解析状态行
    header_section = response.split(b"\r\n\r\n", 1)[0].decode("utf-8", errors="replace")
    first_line = header_section.split("\r\n", 1)[0]
    parts = first_line.split(" ", 2)
    if len(parts) < 2 or parts[1] != "200":
        sock.close()
        raise ConnectionError(f"HTTP CONNECT failed: {first_line!r}")

    # socket现在已建立隧道，可以直接用
    sock.settimeout(None)
    return sock


def create_ssh_client():
    """创建通过HTTP CONNECT代理的SSH客户端"""
    sock = _http_connect_tunnel()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=SSH_HOST,
        port=SSH_PORT,
        username=SSH_USER,
        password=SSH_PASS,
        sock=sock,
        timeout=60,
        banner_timeout=60,
        auth_timeout=60
    )
    return client


def run_remote(cmd):
    """在远程服务器执行命令并返回stdout输出"""
    client = create_ssh_client()
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        exit_code = stdout.channel.recv_exit_status()
        if exit_code != 0 and err.strip():
            print(f"[SSH WARN] exit={exit_code} stderr: {err[:500]}")
        return out
    finally:
        client.close()


def read_remote_file(remote_path):
    """读取远程文件内容"""
    client = create_ssh_client()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.file(remote_path, "r") as f:
                return f.read().decode("utf-8", errors="replace")
        finally:
            sftp.close()
    finally:
        client.close()


def write_remote_file(remote_path, content):
    """写入内容到远程文件"""
    client = create_ssh_client()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.file(remote_path, "w") as f:
                f.write(content)
            # 设置合适的权限
            sftp.chmod(remote_path, 0o644)
        finally:
            sftp.close()
    finally:
        client.close()


def write_remote_json(remote_path, data):
    """写入JSON到远程文件"""
    content = json.dumps(data, ensure_ascii=False, indent=2)
    write_remote_file(remote_path, content)


def read_remote_json(remote_path):
    """从远程文件读取JSON"""
    content = read_remote_file(remote_path)
    if not content.strip():
        return []
    return json.loads(content)


def upload_local_to_remote(local_path, remote_path):
    """上传本地文件到远程"""
    client = create_ssh_client()
    try:
        sftp = client.open_sftp()
        try:
            sftp.put(local_path, remote_path)
            sftp.chmod(remote_path, 0o644)
        finally:
            sftp.close()
    finally:
        client.close()


if __name__ == "__main__":
    # 测试连接
    print("Testing SSH connection...")
    result = run_remote(f"ls -la {REMOTE_DIR} | head -20")
    print(result)
