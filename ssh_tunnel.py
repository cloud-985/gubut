#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SSH 通过 HTTP 代理连接远程服务器，提供远程命令执行与文件传输。"""
import socket
import paramiko

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def _make_tunnel(target_host, target_port):
    """通过 HTTP CONNECT 代理建立到目标主机的隧道 socket。"""
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=25)
    req = f"CONNECT {target_host}:{target_port} HTTP/1.1\r\nHost: {target_host}:{target_port}\r\n\r\n"
    s.sendall(req.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            break
        resp += chunk
    status_line = resp.split(b"\r\n")[0] if resp else b""
    if b"200" not in status_line:
        s.close()
        raise RuntimeError(f"代理 CONNECT 失败: {status_line!r}")
    return s


def _connect():
    sock = _make_tunnel(HOST, PORT)
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(
        HOST, port=PORT, username=USER, password=PASSWORD, sock=sock,
        timeout=25, allow_agent=False, look_for_keys=False,
    )
    return cli


def run_remote(command, timeout=120):
    """在远程服务器执行命令，返回 (exit_code, stdout, stderr)。"""
    cli = _connect()
    try:
        stdin, stdout, stderr = cli.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        code = stdout.channel.recv_exit_status()
        return code, out, err
    finally:
        cli.close()


def get_file(remote_path, local_path):
    """下载远程文件到本地。"""
    cli = _connect()
    try:
        sftp = cli.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
    finally:
        cli.close()


def put_file(local_path, remote_path):
    """上传本地文件到远程。"""
    cli = _connect()
    try:
        sftp = cli.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        cli.close()


if __name__ == "__main__":
    code, out, err = run_remote("echo connected-ok && hostname")
    print("exit:", code)
    print("stdout:", out)
    if err:
        print("stderr:", err)
