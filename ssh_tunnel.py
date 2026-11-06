# -*- coding: utf-8 -*-
"""
SSH 隧道工具：通过 HTTP CONNECT 代理访问远程服务器，执行命令与传输文件。

服务器: 111.91.30.57 (root)
代理:   127.0.0.1:18080
"""
import socket
import paramiko

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080

REMOTE_DIR = "/www/wwwroot/gubut"


def _proxy_connect(host=HOST, port=PORT, timeout=20):
    """通过 HTTP CONNECT 代理建立到目标主机的 TCP 通道。"""
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=timeout)
    req = "CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n".format(
        host=host, port=port
    )
    s.sendall(req.encode("utf-8"))
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            break
        resp += chunk
    status = resp.split(b"\r\n", 1)[0]
    if b"200" not in status:
        raise RuntimeError("代理连接失败: {}".format(status))
    return s


def get_client(timeout=30):
    """返回已认证的 SSHClient。"""
    sock = _proxy_connect(timeout=timeout)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        HOST,
        port=PORT,
        username=USER,
        password=PASSWORD,
        sock=sock,
        timeout=timeout,
        banner_timeout=timeout,
        auth_timeout=timeout,
    )
    return client


def run_remote(command, timeout=60):
    """执行远程命令，返回 (stdout, stderr, exit_code)。"""
    client = get_client()
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        code = stdout.channel.recv_exit_status()
        return out, err, code
    finally:
        client.close()


def read_file(remote_path, timeout=60):
    """读取远程文件内容（文本）。"""
    client = get_client()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.open(remote_path, "r") as f:
                return f.read().decode("utf-8", errors="replace")
        finally:
            sftp.close()
    finally:
        client.close()


def put_file(local_path, remote_path):
    """上传本地文件到远程。"""
    client = get_client()
    try:
        sftp = client.open_sftp()
        try:
            sftp.put(local_path, remote_path)
        finally:
            sftp.close()
    finally:
        client.close()


def get_file(remote_path, local_path):
    """下载远程文件到本地。"""
    client = get_client()
    try:
        sftp = client.open_sftp()
        try:
            sftp.get(remote_path, local_path)
        finally:
            sftp.close()
    finally:
        client.close()


if __name__ == "__main__":
    out, err, code = run_remote("hostname && echo OK")
    print("exit={} out={!r} err={!r}".format(code, out.strip(), err.strip()))
