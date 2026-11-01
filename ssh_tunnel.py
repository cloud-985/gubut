# -*- coding: utf-8 -*-
"""通过 HTTP CONNECT 代理建立到 gubut 服务器的 SSH 连接。

服务器信息:
  服务器: 111.91.30.57
  用户: root
  目录: /www/wwwroot/gubut
  代理: 127.0.0.1:18080 (HTTP CONNECT)
"""
import socket
import paramiko

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"

SITE_DIR = "/www/wwwroot/gubut"


def _open_socket():
    """通过 HTTP CONNECT 代理建立到目标 SSH 端口的原始 TCP 隧道。"""
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=20)
    s.sendall(
        "CONNECT {}:{} HTTP/1.1\r\nHost: {}:{}\r\n\r\n".format(HOST, PORT, HOST, PORT).encode()
    )
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = s.recv(4096)
        if not chunk:
            break
        data += chunk
    return s


def get_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        HOST,
        port=PORT,
        username=USER,
        password=PASSWORD,
        sock=_open_socket(),
        timeout=20,
    )
    return client


def run_remote(cmd, timeout=180):
    """在服务器上执行命令, 返回 (stdout, stderr)。"""
    client = get_client()
    try:
        _in, out, err = client.exec_command(cmd, timeout=timeout)
        return out.read().decode("utf-8", "replace"), err.read().decode("utf-8", "replace")
    finally:
        client.close()


def upload(local_path, remote_path):
    client = get_client()
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        client.close()


def download(remote_path, local_path):
    client = get_client()
    try:
        sftp = client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
    finally:
        client.close()


if __name__ == "__main__":
    out, err = run_remote("hostname && date '+%Y-%m-%d %H:%M:%S %Z'")
    print("STDOUT:", out)
    print("STDERR:", err)
