#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSH 隧道工具：通过 HTTP 代理连接远程服务器
服务器: 111.91.30.57 root / www/wwwroot/gubut
代理: 127.0.0.1:18080
"""

import paramiko
import socket
import os
import time
import json

SSH_HOST = "111.91.30.57"
SSH_PORT = 22
SSH_USER = "root"
SSH_PASS = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080
REMOTE_DIR = "/www/wwwroot/gubut"


def http_connect_tunnel(target_host, target_port, proxy_host, proxy_port):
    """通过 HTTP CONNECT 创建隧道 socket"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((proxy_host, proxy_port))
    connect_request = f"CONNECT {target_host}:{target_port} HTTP/1.1\r\nHost: {target_host}:{target_port}\r\n\r\n"
    sock.sendall(connect_request.encode())
    response = b""
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    if b"200" not in response.split(b"\r\n")[0]:
        raise Exception(f"Proxy CONNECT failed: {response[:200]}")
    return sock


def get_ssh_client():
    """建立 SSH 连接（通过代理）"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        sock = http_connect_tunnel(SSH_HOST, SSH_PORT, PROXY_HOST, PROXY_PORT)
        client.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USER,
            password=SSH_PASS,
            sock=sock,
            timeout=30,
            banner_timeout=30,
            auth_timeout=30,
        )
        return client
    except Exception as e:
        # 直连 fallback
        try:
            client.connect(
                hostname=SSH_HOST,
                port=SSH_PORT,
                username=SSH_USER,
                password=SSH_PASS,
                timeout=30,
                banner_timeout=30,
                auth_timeout=30,
            )
            return client
        except Exception as e2:
            raise Exception(f"SSH 连接失败(代理:{e}, 直连:{e2})")


def run_remote(cmd, timeout=60):
    """执行远程命令并返回 stdout, stderr, exit_code"""
    client = get_ssh_client()
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        return out, err, exit_code
    finally:
        client.close()


def read_remote_file(remote_path):
    """读取远程文件内容为字符串"""
    client = get_ssh_client()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.file(remote_path, "r") as f:
                return f.read().decode("utf-8", errors="replace")
        finally:
            sftp.close()
    finally:
        client.close()


def write_remote_file(remote_path, content, mode=0o644):
    """写入内容到远程文件"""
    client = get_ssh_client()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.file(remote_path, "w") as f:
                f.write(content)
            sftp.chmod(remote_path, mode)
        finally:
            sftp.close()
    finally:
        client.close()


def upload_file(local_path, remote_path, mode=0o644):
    """上传本地文件到远程"""
    client = get_ssh_client()
    try:
        sftp = client.open_sftp()
        try:
            sftp.put(local_path, remote_path)
            sftp.chmod(remote_path, mode)
        finally:
            sftp.close()
    finally:
        client.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 ssh_tunnel.py <command>")
        print("  test        - 测试连接")
        print("  ls [path]   - 列出目录")
        print("  cat <path>  - 查看文件")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "test":
        out, err, code = run_remote(f"echo ok && ls {REMOTE_DIR} | head -20")
        print("STDOUT:", out)
        print("STDERR:", err)
        print("EXIT:", code)
    elif cmd == "ls":
        path = sys.argv[2] if len(sys.argv) > 2 else REMOTE_DIR
        out, err, code = run_remote(f"ls -la {path}")
        print(out)
        if err:
            print("ERR:", err)
    elif cmd == "cat":
        path = sys.argv[2]
        out, err, code = run_remote(f"cat {path}")
        print(out)
        if err:
            print("ERR:", err)
