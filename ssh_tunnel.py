#!/usr/bin/env python3
"""SSH tunnel helper: connect to remote server through HTTP proxy and run commands."""
import socket
import sys
import io

import paramiko

REMOTE_HOST = "111.91.30.57"
REMOTE_PORT = 22
REMOTE_USER = "root"
REMOTE_PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def _open_proxy_socket(host, port, proxy_host=PROXY_HOST, proxy_port=PROXY_PORT):
    """Open a raw socket tunnelled through the HTTP proxy using CONNECT."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect((proxy_host, proxy_port))
    req = "CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n".format(
        host=host, port=port
    ).encode("latin-1")
    s.sendall(req)
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            break
        resp += chunk
    status_line = resp.split(b"\r\n", 1)[0].decode("latin-1", "replace")
    if "200" not in status_line:
        s.close()
        raise RuntimeError("proxy CONNECT failed: " + status_line)
    s.settimeout(60)
    return s


def get_client():
    """Create and return a connected paramiko SSHClient."""
    sock = _open_proxy_socket(REMOTE_HOST, REMOTE_PORT)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        REMOTE_HOST,
        port=REMOTE_PORT,
        username=REMOTE_USER,
        password=REMOTE_PASSWORD,
        sock=sock,
        timeout=30,
        look_for_keys=False,
        allow_agent=False,
    )
    return client


def run_remote(command, timeout=120):
    """Run a command on the remote server and return (stdout, stderr, exit_code)."""
    client = get_client()
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        code = stdout.channel.recv_exit_status()
        return out, err, code
    finally:
        client.close()


def put_file(local_path, remote_path):
    """Upload a local file to the remote server."""
    client = get_client()
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        return True
    finally:
        client.close()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "echo ok"
    out, err, code = run_remote(cmd)
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)
