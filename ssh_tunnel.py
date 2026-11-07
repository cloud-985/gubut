#!/usr/bin/env python3
"""SSH helper that connects to the production server through the HTTP CONNECT proxy."""
import socket
import paramiko

HOST = '111.91.30.57'
PORT = 22
USER = 'root'
PASSWORD = '722bza2MtAmwF3Pm'
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 18080


def _proxy_socket(host=HOST, port=PORT, timeout=30):
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=timeout)
    req = f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n"
    s.sendall(req.encode())
    data = b''
    while b'\r\n\r\n' not in data:
        chunk = s.recv(4096)
        if not chunk:
            break
        data += chunk
    if b'200' not in data.split(b'\r\n')[0]:
        s.close()
        raise RuntimeError(f'proxy CONNECT failed: {data[:200]!r}')
    return s


def get_client(timeout=30):
    sock = _proxy_socket(timeout=timeout)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        HOST,
        port=PORT,
        username=USER,
        password=PASSWORD,
        sock=sock,
        timeout=timeout,
        look_for_keys=False,
        allow_agent=False,
    )
    return client


def run_remote(cmd, timeout=120):
    client = get_client(timeout=timeout)
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode('utf-8', 'replace')
        err = stderr.read().decode('utf-8', 'replace')
        code = stdout.channel.recv_exit_status()
        return {'stdout': out, 'stderr': err, 'exit_code': code}
    finally:
        client.close()


def get_file(remote_path, local_path):
    client = get_client()
    try:
        sftp = client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
    finally:
        client.close()


def put_file(local_path, remote_path):
    client = get_client()
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        client.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        print(run_remote(sys.argv[1]))
    else:
        r = run_remote('echo ok && hostname && pwd')
        print(r['stdout'])
        print('EXIT', r['exit_code'])
        if r['stderr']:
            print('STDERR', r['stderr'])
