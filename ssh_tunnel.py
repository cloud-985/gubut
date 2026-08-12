#!/usr/bin/env python3
"""通过 HTTP 代理隧道 SSH 连接到远程服务器,执行命令并上传文件."""
import sys
import socket
import paramiko

HOST = "111.91.30.57"
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PORT = 22

# HTTP 代理
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def make_proxy_socket(target_host, target_port, timeout=20):
    """通过 HTTP CONNECT 代理建立到目标的 TCP 隧道。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((PROXY_HOST, PROXY_PORT))
    req = (
        f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
        f"Host: {target_host}:{target_port}\r\n"
        f"User-Agent: seo-agent/1.0\r\n"
        f"\r\n"
    )
    s.sendall(req.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            raise RuntimeError("代理关闭连接")
        resp += chunk
    status_line = resp.split(b"\r\n")[0].decode("utf-8", errors="replace")
    if " 200 " not in status_line:
        raise RuntimeError(f"代理 CONNECT 失败: {status_line}")
    return s


def get_transport():
    """建立 SSH Transport(通过代理隧道)."""
    sock = make_proxy_socket(HOST, PORT)
    transport = paramiko.Transport(sock)
    transport.set_keepalive(30)
    transport.connect(username=USER, password=PASSWORD)
    return transport


def run_remote(cmd, timeout=120):
    """执行远程命令并返回 (exit_code, stdout, stderr)."""
    transport = get_transport()
    try:
        chan = transport.open_session()
        chan.settimeout(timeout)
        chan.exec_command(cmd)
        out = b""
        err = b""
        while not chan.exit_status_ready():
            if chan.recv_ready():
                out += chan.recv(65536)
            if chan.recv_stderr_ready():
                err += chan.recv_stderr(65536)
        # 读取剩余
        while chan.recv_ready():
            out += chan.recv(65536)
        while chan.recv_stderr_ready():
            err += chan.recv_stderr(65536)
        code = chan.recv_exit_status()
        return code, out.decode("utf-8", errors="replace"), err.decode("utf-8", errors="replace")
    finally:
        transport.close()


def upload_file(local_path, remote_path, timeout=60):
    """通过 SFTP 上传文件."""
    transport = get_transport()
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, remote_path)
        sftp.close()
        return True
    finally:
        transport.close()


if __name__ == "__main__":
    # 测试连接
    print(f"正在通过代理连接 {USER}@{HOST}:{PORT} ...")
    code, out, err = run_remote("echo 'SSH连接成功'; whoami; uname -a; echo '---'; ls -la /www/wwwroot/sedgo/ 2>&1 | head -30")
    print(out)
    if err:
        print("STDERR:", err, file=sys.stderr)
    sys.exit(code)
