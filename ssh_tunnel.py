#!/usr/bin/env python3
"""SSH 通过 HTTP CONNECT 代理连接到生产服务器并执行远程命令。"""
import socket
import paramiko

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def _connect_via_http_connect(target_host, target_port, proxy_host=PROXY_HOST, proxy_port=PROXY_PORT, timeout=30):
    """通过 HTTP CONNECT 代理建立到目标主机的 TCP 通道。"""
    sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    connect_req = f"CONNECT {target_host}:{target_port} HTTP/1.1\r\nHost: {target_host}:{target_port}\r\n\r\n"
    sock.sendall(connect_req.encode("utf-8"))
    # 读取代理响应头
    response = b""
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("代理连接被提前关闭")
        response += chunk
    head, _, _ = response.partition(b"\r\n\r\n")
    status_line = head.split(b"\r\n", 1)[0].decode("utf-8", "ignore")
    if " 200 " not in " " + status_line + " ":
        raise ConnectionError(f"代理 CONNECT 失败: {status_line}")
    return sock


def _new_client():
    sock = _connect_via_http_connect(HOST, PORT)
    transport = paramiko.Transport(sock)
    transport.connect(username=USER, password=PASSWORD)
    return transport


def run_remote(command, timeout=120):
    """在远程服务器执行命令并返回 (stdout, stderr, exit_code)。"""
    transport = _new_client()
    try:
        channel = transport.open_session()
        channel.settimeout(timeout)
        channel.exec_command(command)
        stdout = b""
        stderr = b""
        while True:
            if channel.recv_ready():
                stdout += channel.recv(65536)
            if channel.recv_stderr_ready():
                stderr += channel.recv_stderr(65536)
            if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready():
                break
            if channel.closed:
                break
        # 收尾读取
        while channel.recv_ready():
            stdout += channel.recv(65536)
        while channel.recv_stderr_ready():
            stderr += channel.recv_stderr(65536)
        exit_code = channel.recv_exit_status()
        return stdout.decode("utf-8", "replace"), stderr.decode("utf-8", "replace"), exit_code
    finally:
        transport.close()


def get_file_bytes(remote_path, timeout=60):
    """通过 SFTP 读取远程文件内容（bytes）。"""
    transport = _new_client()
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        with sftp.open(remote_path, "rb") as f:
            return f.read()
    finally:
        transport.close()


def put_file_bytes(remote_path, data, timeout=60):
    """通过 SFTP 写入远程文件。"""
    transport = _new_client()
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        with sftp.open(remote_path, "wb") as f:
            f.write(data)
    finally:
        transport.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        out, err, code = run_remote(sys.argv[1])
        print(out, end="")
        if err:
            print("STDERR:", err, file=sys.stderr)
        sys.exit(code)
    else:
        out, err, code = run_remote("whoami && pwd && ls /www/wwwroot/gubut")
        print("=== stdout ===")
        print(out)
        print("=== stderr ===")
        print(err)
        print("=== exit ===", code)
