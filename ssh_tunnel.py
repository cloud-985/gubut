# -*- coding: utf-8 -*-
"""SSH 隧道工具：通过 HTTP 代理 127.0.0.1:18080 连接服务器并执行远程命令。"""
import socket
import sys

import paramiko

SERVER_HOST = "111.91.30.57"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def _connect_via_proxy():
    """通过 HTTP CONNECT 代理建立到目标主机的 socket。"""
    sock = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=30)
    connect_req = (
        f"CONNECT {SERVER_HOST}:{SERVER_PORT} HTTP/1.1\r\n"
        f"Host: {SERVER_HOST}:{SERVER_PORT}\r\n"
        "Proxy-Connection: keep-alive\r\n\r\n"
    )
    sock.sendall(connect_req.encode("utf-8"))
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    if b"200" not in data.split(b"\r\n", 1)[0]:
        raise RuntimeError(f"代理连接失败: {data!r}")
    return sock


def get_client():
    """建立并返回一个已认证的 SSH 客户端。"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sock = _connect_via_proxy()
    client.connect(
        SERVER_HOST,
        port=SERVER_PORT,
        username=SERVER_USER,
        password=SERVER_PASSWORD,
        sock=sock,
        timeout=30,
        banner_timeout=30,
        auth_timeout=30,
        look_for_keys=False,
        allow_agent=False,
    )
    return client


def run_remote(command, timeout=120):
    """在远程服务器执行命令，返回 (stdout, stderr, exit_code)。"""
    client = get_client()
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        exit_code = stdout.channel.recv_exit_status()
        return out, err, exit_code
    finally:
        client.close()


def put_file(local_path, remote_path):
    """通过 SFTP 上传本地文件到服务器。"""
    client = get_client()
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        client.close()


def get_file(remote_path, local_path):
    """通过 SFTP 下载服务器文件到本地。"""
    client = get_client()
    try:
        sftp = client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
    finally:
        client.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 ssh_tunnel.py '<远程命令>'")
        sys.exit(1)
    cmd = sys.argv[1]
    out, err, code = run_remote(cmd)
    print(out)
    if err:
        print("STDERR:", err, file=sys.stderr)
    sys.exit(code)
