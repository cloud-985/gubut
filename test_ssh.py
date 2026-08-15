#!/usr/bin/env python3
"""Test SSH connection through HTTP proxy."""
import socket
import paramiko
import sys

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080
SSH_HOST = "111.91.30.57"
SSH_PORT = 22
SSH_USER = "root"
SSH_PASS = "722bza2MtAmwF3Pm"


def make_proxy_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    sock.connect((PROXY_HOST, PROXY_PORT))
    req = f"CONNECT {SSH_HOST}:{SSH_PORT} HTTP/1.1\r\nHost: {SSH_HOST}:{SSH_PORT}\r\n\r\n"
    sock.send(req.encode())
    resp = sock.recv(4096).decode(errors="ignore")
    print("Proxy response:", resp[:200])
    if "200" not in resp.split("\r\n")[0]:
        raise RuntimeError(f"Proxy CONNECT failed: {resp[:200]}")
    return sock


def main():
    sock = make_proxy_socket()
    transport = paramiko.Transport(sock)
    transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    transport.connect(username=SSH_USER, password=SSH_PASS)
    print("SSH transport connected:", transport.is_authenticated())
    chan = transport.open_session()
    chan.exec_command("hostname && pwd && ls /www/wwwroot/gubut/ | head -30")
    out = b""
    while True:
        if chan.recv_ready():
            out += chan.recv(4096)
        if chan.exit_status_ready() and not chan.recv_ready():
            break
    print("OUTPUT:")
    print(out.decode(errors="ignore"))
    chan.close()
    transport.close()


if __name__ == "__main__":
    main()
