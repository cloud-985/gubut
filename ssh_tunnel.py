# -*- coding: utf-8 -*-
"""SSH 隧道工具：通过本地 HTTP 代理连接远程服务器，提供 run_remote / get_file / put_file。

用法：
    from ssh_tunnel import run_remote, get_file, put_file, HOST, REMOTE_DIR

服务器: 111.91.30.57  目录: /www/wwwroot/gubut
代理: 127.0.0.1:18080 (HTTP CONNECT)
"""
import os
import socket
import time
import paramiko

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
REMOTE_DIR = "/www/wwwroot/gubut"

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080

# 远程命令执行超时（秒）
CMD_TIMEOUT = 60


def _proxy_socket(target_host, target_port, timeout=20):
    """通过 HTTP 代理建立到 target_host:target_port 的 TCP 隧道。"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((PROXY_HOST, PROXY_PORT))
    connect_req = (
        f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
        f"Host: {target_host}:{target_port}\r\n"
        f"Proxy-Connection: keep-alive\r\n\r\n"
    ).encode()
    sock.sendall(connect_req)
    # 读取代理响应
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = sock.recv(4096)
        if not chunk:
            break
        resp += chunk
        if len(resp) > 8192:
            break
    head = resp.split(b"\r\n", 1)[0].decode("latin-1", "ignore")
    if " 200 " not in head:
        sock.close()
        raise RuntimeError(f"代理 CONNECT 失败: {head}")
    return sock


def _connect(retry=3):
    last_err = None
    for i in range(retry):
        try:
            sock = _proxy_socket(HOST, PORT, timeout=25)
            transport = paramiko.Transport(sock)
            transport.set_keepalive(30)
            transport.use_compression = True
            transport.connect(username=USER, password=PASSWORD)
            return transport
        except Exception as e:  # noqa
            last_err = e
            time.sleep(2 + i * 2)
    raise RuntimeError(f"SSH 连接失败 ({HOST}): {last_err}")


def run_remote(cmd, timeout=CMD_TIMEOUT, check=False):
    """在远程服务器执行命令，返回 (rc, stdout, stderr)。"""
    transport = _connect()
    chan = None
    try:
        chan = transport.open_session()
        chan.settimeout(timeout)
        chan.exec_command(cmd)
        out = b""
        err = b""
        while True:
            if chan.recv_ready():
                out += chan.recv(65536)
            if chan.recv_stderr_ready():
                err += chan.recv_stderr(65536)
            if chan.exit_status_ready() and not chan.recv_ready() and not chan.recv_stderr_ready():
                break
        # 收尾
        while chan.recv_ready():
            out += chan.recv(65536)
        while chan.recv_stderr_ready():
            err += chan.recv_stderr(65536)
        rc = chan.recv_exit_status()
        if check and rc != 0:
            raise RuntimeError(f"命令执行失败 rc={rc}: {err.decode('utf-8','ignore')[:500]}")
        return rc, out.decode("utf-8", "ignore"), err.decode("utf-8", "ignore")
    finally:
        if chan:
            chan.close()
        transport.close()


def get_file(remote_path, local_path=None):
    """下载远程文件。"""
    transport = _connect()
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        data = sftp.open(remote_path, "rb").read()
        if local_path:
            with open(local_path, "wb") as f:
                f.write(data)
        return data
    finally:
        transport.close()


def put_file(local_path, remote_path):
    """上传本地文件到远程。"""
    transport = _connect()
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, remote_path)
        return True
    finally:
        transport.close()


def put_bytes(data, remote_path):
    """直接写入字节到远程文件。"""
    transport = _connect()
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        with sftp.open(remote_path, "wb") as f:
            f.write(data)
        return True
    finally:
        transport.close()


if __name__ == "__main__":
    print("测试 SSH 连接 ...")
    rc, out, err = run_remote("whoami; hostname; date '+%Y-%m-%d %H:%M:%S'; echo ---; ls -la " + REMOTE_DIR + " | head -20")
    print("rc:", rc)
    print(out)
    if err:
        print("STDERR:", err)
