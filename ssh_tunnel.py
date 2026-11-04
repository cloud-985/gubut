#!/usr/bin/env python3
"""SSH 隧道工具：通过 HTTP 代理 127.0.0.1:18080 连接远程服务器并执行命令。

用法:
    from ssh_tunnel import run_remote, run_remote_sudo
    out, err, code = run_remote("ls -la /www/wwwroot/gubut")
"""
import socket
import io

import paramiko

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def _open_proxy_socket(target_host=HOST, target_port=PORT, timeout=30):
    """通过 HTTP CONNECT 代理建立到目标主机的 TCP 连接。"""
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=timeout)
    s.settimeout(timeout)
    connect_req = (
        f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
        f"Host: {target_host}:{target_port}\r\n"
        f"Proxy-Connection: Keep-Alive\r\n\r\n"
    )
    s.sendall(connect_req.encode("utf-8"))
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = s.recv(4096)
        if not chunk:
            break
        data += chunk
    head, _, _rest = data.partition(b"\r\n\r\n")
    head_str = head.decode("utf-8", "ignore")
    if "200" not in head_str.split("\r\n")[0]:
        s.close()
        raise ConnectionError(f"代理 CONNECT 失败: {head_str}")
    return s


def _get_client():
    sock = _open_proxy_socket()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        HOST,
        port=PORT,
        username=USER,
        password=PASSWORD,
        sock=sock,
        timeout=30,
        banner_timeout=30,
        auth_timeout=30,
        allow_agent=False,
        look_for_keys=False,
    )
    return client


def run_remote(command, timeout=120):
    """在远程服务器执行命令，返回 (stdout, stderr, exit_code)。"""
    client = _get_client()
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", "ignore")
        err = stderr.read().decode("utf-8", "ignore")
        code = stdout.channel.recv_exit_status()
        return out, err, code
    finally:
        client.close()


def put_file(local_path, remote_path):
    """通过 SFTP 上传本地文件到远程服务器。"""
    client = _get_client()
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        client.close()


def get_file(remote_path, local_path):
    """通过 SFTP 下载远程文件到本地。"""
    client = _get_client()
    try:
        sftp = client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
    finally:
        client.close()


def run_remote_sudo(command, timeout=120):
    """以 root 执行（本环境已用 root 登录，等价于 run_remote）。"""
    return run_remote(command, timeout=timeout)


if __name__ == "__main__":
    out, err, code = run_remote("echo OK && whoami && ls /www/wwwroot/gubut | head -20")
    print("exit:", code)
    print("stdout:\n", out)
    if err.strip():
        print("stderr:\n", err)
