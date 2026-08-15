#!/usr/bin/env python3
"""SSH tunnel wrapper - reusable module for accessing gubut.com server."""
import socket
import paramiko
import json
import time

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080
SSH_HOST = "111.91.30.57"
SSH_PORT = 22
SSH_USER = "root"
SSH_PASS = "722bza2MtAmwF3Pm"


class SSHTunnel:
    def __init__(self):
        self.client = None

    def _proxy_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(60)
        sock.connect((PROXY_HOST, PROXY_PORT))
        req = f"CONNECT {SSH_HOST}:{SSH_PORT} HTTP/1.1\r\nHost: {SSH_HOST}:{SSH_PORT}\r\n\r\n"
        sock.send(req.encode())
        resp = sock.recv(4096).decode(errors="ignore")
        if "200" not in resp.split("\r\n")[0]:
            raise RuntimeError(f"Proxy CONNECT failed: {resp[:200]}")
        return sock

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sock = self._proxy_socket()
        self.client.connect(
            SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS,
            sock=sock, look_for_keys=False, allow_agent=False, timeout=60
        )
        return self.client

    def run_remote(self, cmd, timeout=120):
        if self.client is None:
            self.connect()
        stdin, stdout, stderr = self.client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode(errors="ignore")
        err = stderr.read().decode(errors="ignore")
        rc = stdout.channel.recv_exit_status()
        return rc, out, err

    def get_file(self, remote_path):
        rc, out, err = self.run_remote(f"cat '{remote_path}'")
        if rc != 0:
            raise RuntimeError(f"get_file failed: {err}")
        return out

    def put_file(self, local_path, remote_path):
        if self.client is None:
            self.connect()
        sftp = self.client.open_sftp()
        try:
            sftp.put(local_path, remote_path)
        finally:
            sftp.close()

    def close(self):
        if self.client:
            self.client.close()
            self.client = None


ssh_tunnel = SSHTunnel()


if __name__ == "__main__":
    rc, out, err = ssh_tunnel.run_remote("hostname && pwd && ls /www/wwwroot/gubut/ | head -30")
    print("rc=", rc)
    print("OUT:")
    print(out)
    if err:
        print("ERR:", err)
    ssh_tunnel.close()
