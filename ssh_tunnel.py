import socket

import paramiko

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 18080
SSH_HOST = '111.91.30.57'
SSH_PORT = 22
SSH_USER = 'root'
SSH_PASSWORD = '722bza2MtAmwF3Pm'


def _proxy_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect((PROXY_HOST, PROXY_PORT))
    req = 'CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n'.format(host=host, port=port)
    s.sendall(req.encode())
    resp = b''
    while b'\r\n\r\n' not in resp:
        chunk = s.recv(4096)
        if not chunk:
            break
        resp += chunk
    if b'200' not in resp.split(b'\r\n')[0]:
        raise RuntimeError('代理连接失败: ' + repr(resp))
    return s


def get_client():
    sock = _proxy_socket(SSH_HOST, SSH_PORT)
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(
        SSH_HOST,
        port=SSH_PORT,
        username=SSH_USER,
        password=SSH_PASSWORD,
        sock=sock,
        timeout=30,
        banner_timeout=30,
        auth_timeout=30,
    )
    return cli


def run_remote(cmd, timeout=180):
    cli = get_client()
    try:
        stdin, stdout, stderr = cli.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode('utf-8', 'replace')
        err = stderr.read().decode('utf-8', 'replace')
        return out, err
    finally:
        cli.close()


def read_file(remote_path):
    cli = get_client()
    try:
        sftp = cli.open_sftp()
        with sftp.open(remote_path, 'r') as f:
            data = f.read().decode('utf-8', 'replace')
        sftp.close()
        return data
    finally:
        cli.close()


def put_file(local_path, remote_path):
    cli = get_client()
    try:
        sftp = cli.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        cli.close()
