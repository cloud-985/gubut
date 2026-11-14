#!/usr/bin/env python3
"""SSH 隧道工具：通过 HTTP 代理连接远程服务器并执行命令 / 传输文件。

用法：
    import ssh_tunnel
    out, err = ssh_tunnel.run_remote("ls -la /www/wwwroot/gubut")
    ssh_tunnel.upload("/workspace/ai_article.json", "/www/wwwroot/gubut/ai_article.json")
    ssh_tunnel.download("/www/wwwroot/gubut/pending-articles.json", "/workspace/pending-articles.json")
"""

import socket
import paramiko

HOST = "111.91.30.57"
PORT = 22
USERNAME = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080
TIMEOUT = 60


def _http_connect_tunnel(proxy_host, proxy_port, target_host, target_port, timeout=TIMEOUT):
    """通过 HTTP 代理的 CONNECT 方法建立到目标主机的隧道 socket。"""
    s = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    s.settimeout(timeout)
    req = (
        "CONNECT {host}:{port} HTTP/1.1\r\n"
        "Host: {host}:{port}\r\n"
        "Proxy-Connection: keep-alive\r\n"
        "\r\n"
    ).format(host=target_host, port=target_port)
    s.sendall(req.encode("ascii"))

    data = b""
    while b"\r\n\r\n" not in data:
        chunk = s.recv(4096)
        if not chunk:
            break
        data += chunk

    status_line = data.split(b"\r\n", 1)[0]
    if b"200" not in status_line:
        s.close()
        raise RuntimeError("HTTP CONNECT 失败: " + status_line.decode("utf-8", errors="replace"))
    return s


def _connect():
    sock = _http_connect_tunnel(PROXY_HOST, PROXY_PORT, HOST, PORT)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        sock=sock,
        timeout=TIMEOUT,
        banner_timeout=TIMEOUT,
        auth_timeout=TIMEOUT,
    )
    return client


def run_remote(command, timeout=TIMEOUT):
    """在远程服务器执行命令，返回 (stdout, stderr) 字符串元组。"""
    client = _connect()
    try:
        _stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        return out, err
    finally:
        client.close()


def upload(local_path, remote_path):
    """通过 SFTP 上传本地文件到远程。"""
    client = _connect()
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        client.close()


def download(remote_path, local_path):
    """通过 SFTP 下载远程文件到本地。"""
    client = _connect()
    try:
        sftp = client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
    finally:
        client.close()


if __name__ == "__main__":
    out, err = run_remote("echo SSH_TUNNEL_OK && hostname")
    print(out.strip())
    if err.strip():
        print("[stderr]", err.strip())
