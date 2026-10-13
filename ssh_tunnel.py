import socket
import paramiko

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def _make_sock(timeout=30):
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=timeout)
    req = f"CONNECT {HOST}:{PORT} HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n\r\n"
    s.sendall(req.encode())
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = s.recv(4096)
        if not chunk:
            break
        data += chunk
    status = data.split(b"\r\n")[0] if data else b""
    if b"200" not in status:
        raise ConnectionError(f"proxy connect failed: {status!r}")
    return s


def run_remote(command, timeout=60):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        HOST,
        port=PORT,
        username=USER,
        password=PASSWORD,
        sock=_make_sock(),
        timeout=timeout,
        banner_timeout=30,
        auth_timeout=30,
    )
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        code = stdout.channel.recv_exit_status()
        return code, out, err
    finally:
        client.close()


def upload_file(local_path, remote_path, timeout=60):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        HOST,
        port=PORT,
        username=USER,
        password=PASSWORD,
        sock=_make_sock(),
        timeout=timeout,
        banner_timeout=30,
        auth_timeout=30,
    )
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        client.close()


if __name__ == "__main__":
    code, out, err = run_remote("hostname")
    print(code)
    print(out)
    print(err)
