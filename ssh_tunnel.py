#!/usr/bin/env python3
"""通过 HTTP CONNECT 代理建立 SSH 连接并执行远程命令的工具模块。"""
import socket
import paramiko

SSH_CONFIG = {
    "host": "111.91.30.57",
    "port": 22,
    "username": "root",
    "password": "722bza2MtAmwF3Pm",
    "proxy_host": "127.0.0.1",
    "proxy_port": 18080,
}


def _http_connect_tunnel(host, port, proxy_host, proxy_port, timeout=30):
    """建立到目标主机的 HTTP CONNECT 隧道，返回已连接的 socket。"""
    sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    connect_req = f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n"
    sock.sendall(connect_req.encode("ascii"))
    response = b""
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            raise RuntimeError("代理在 CONNECT 阶段关闭连接")
        response += chunk
    status_line = response.split(b"\r\n", 1)[0].decode("ascii", "ignore")
    if " 200 " not in status_line:
        raise RuntimeError(f"代理 CONNECT 失败: {status_line}")
    return sock


def _get_client():
    sock = _http_connect_tunnel(
        SSH_CONFIG["host"],
        SSH_CONFIG["port"],
        SSH_CONFIG["proxy_host"],
        SSH_CONFIG["proxy_port"],
    )
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        SSH_CONFIG["host"],
        port=SSH_CONFIG["port"],
        username=SSH_CONFIG["username"],
        password=SSH_CONFIG["password"],
        sock=sock,
        timeout=30,
        allow_agent=False,
        look_for_keys=False,
    )
    return client


def run_remote(command, timeout=120):
    """在远程服务器执行命令，返回 (stdout, stderr, exit_code)。"""
    client = _get_client()
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        exit_code = stdout.channel.recv_exit_status()
        return out, err, exit_code
    finally:
        client.close()


def read_remote_file(path):
    """读取远程文件内容，返回字符串（文件不存在时返回 None）。"""
    client = _get_client()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.open(path, "r") as f:
                return f.read().decode("utf-8", "replace")
        except FileNotFoundError:
            return None
        finally:
            sftp.close()
    finally:
        client.close()


def write_remote_file(path, content):
    """将字符串内容写入远程文件。"""
    client = _get_client()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.open(path, "w") as f:
                f.write(content)
        finally:
            sftp.close()
    finally:
        client.close()


if __name__ == "__main__":
    out, err, code = run_remote("echo OK && uname -a")
    print("exit:", code)
    print("stdout:", out)
    print("stderr:", err)
