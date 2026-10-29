#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SSH 隧道工具：通过 HTTP 代理 (CONNECT) 连接远程服务器执行命令与传输文件。"""
import socket
import paramiko

SERVER_HOST = "111.91.30.57"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "722bza2MtAmwF3Pm"

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080

REMOTE_DIR = "/www/wwwroot/gubut"

TIMEOUT = 60


def _connect_via_proxy(host, port):
    """建立到目标主机端口的 CONNECT 隧道，返回已就绪的 socket。"""
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=30)
    req = "CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n".format(
        host=host, port=port
    )
    s.sendall(req.encode("utf-8"))
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = s.recv(4096)
        if not chunk:
            break
        data += chunk
    status_line = data.split(b"\r\n", 1)[0]
    if b"200" not in status_line:
        s.close()
        raise RuntimeError("代理 CONNECT 失败: %r" % status_line[:200])
    return s


def _get_client():
    sock = _connect_via_proxy(SERVER_HOST, SERVER_PORT)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=SERVER_HOST,
        port=SERVER_PORT,
        username=SERVER_USER,
        password=SERVER_PASSWORD,
        sock=sock,
        timeout=TIMEOUT,
        banner_timeout=TIMEOUT,
        auth_timeout=TIMEOUT,
        allow_agent=False,
        look_for_keys=False,
    )
    return client


def run_remote(cmd):
    """在远程服务器执行命令，返回 (exit_code, stdout, stderr)。"""
    client = _get_client()
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=TIMEOUT)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        code = stdout.channel.recv_exit_status()
        return code, out, err
    finally:
        client.close()


def sftp_put(local_path, remote_path):
    """上传本地文件到远程服务器。"""
    sock = _connect_via_proxy(SERVER_HOST, SERVER_PORT)
    transport = paramiko.Transport(sock)
    transport.connect(username=SERVER_USER, password=SERVER_PASSWORD)
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, remote_path)
    finally:
        transport.close()


def sftp_get(remote_path, local_path):
    """从远程服务器下载文件到本地。"""
    sock = _connect_via_proxy(SERVER_HOST, SERVER_PORT)
    transport = paramiko.Transport(sock)
    transport.connect(username=SERVER_USER, password=SERVER_PASSWORD)
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_path, local_path)
    finally:
        transport.close()


if __name__ == "__main__":
    code, out, err = run_remote("echo OK && whoami && pwd")
    print("exit=%s" % code)
    print("stdout:\n%s" % out)
    print("stderr:\n%s" % err)
