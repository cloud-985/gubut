import socket
import paramiko

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def _http_connect_socket():
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=30)
    req = "CONNECT {}:{} HTTP/1.1\r\nHost: {}:{}\r\nProxy-Connection: Keep-Alive\r\n\r\n".format(
        HOST, PORT, HOST, PORT
    )
    s.sendall(req.encode("ascii"))
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = s.recv(4096)
        if not chunk:
            raise RuntimeError("proxy closed connection during CONNECT")
        buf += chunk
        if len(buf) > 65536:
            raise RuntimeError("proxy response too large")
    head, _, rest = buf.partition(b"\r\n\r\n")
    status_line = head.split(b"\r\n", 1)[0].decode("ascii", "replace")
    if "200" not in status_line:
        raise RuntimeError("proxy CONNECT failed: {}".format(status_line))
    return s


def connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sock = _http_connect_socket()
    client.connect(
        hostname=HOST,
        port=PORT,
        username=USER,
        password=PASSWORD,
        sock=sock,
        banner_timeout=30,
        auth_timeout=30,
        timeout=30,
    )
    return client


def run_remote(command, timeout=120):
    client = connect()
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        code = stdout.channel.recv_exit_status()
        return out, err, code
    finally:
        client.close()


def get_file(remote_path):
    client = connect()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.open(remote_path, "rb") as f:
                return f.read()
        finally:
            sftp.close()
    finally:
        client.close()


def put_file(local_path, remote_path):
    client = connect()
    try:
        sftp = client.open_sftp()
        try:
            sftp.put(local_path, remote_path)
        finally:
            sftp.close()
    finally:
        client.close()


if __name__ == "__main__":
    out, err, code = run_remote("echo OK && whoami && pwd")
    print("exit:", code)
    print("stdout:", out)
    print("stderr:", err)
