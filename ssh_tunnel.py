import socket
import paramiko

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080
SERVER_HOST = "111.91.30.57"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "722bza2MtAmwF3Pm"


def _connect():
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=30)
    s.sendall(
        ("CONNECT %s:%d HTTP/1.1\r\nHost: %s:%d\r\n\r\n"
         % (SERVER_HOST, SERVER_PORT, SERVER_HOST, SERVER_PORT)).encode("ascii")
    )
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = s.recv(4096)
        if not chunk:
            break
        buf += chunk
    status_line = buf.split(b"\r\n", 1)[0]
    if b"200" not in status_line:
        s.close()
        raise RuntimeError("代理连接失败: %r" % buf)
    transport = paramiko.Transport(s)
    transport.connect(username=SERVER_USER, password=SERVER_PASSWORD)
    client = paramiko.SSHClient()
    client._transport = transport
    return client


def run_remote(command, timeout=180):
    client = _connect()
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        code = stdout.channel.recv_exit_status()
        return code, out, err
    finally:
        client.close()


def put_file(local_path, remote_path):
    client = _connect()
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        client.close()


def get_file(remote_path, local_path):
    client = _connect()
    try:
        sftp = client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
    finally:
        client.close()
