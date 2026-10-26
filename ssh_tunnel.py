import socket
import paramiko

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080
REMOTE_HOST = "111.91.30.57"
REMOTE_PORT = 22
REMOTE_USER = "root"
REMOTE_PASSWORD = "722bza2MtAmwF3Pm"
REMOTE_BASE = "/www/wwwroot/gubut"


def _open_proxy_socket(host, port, timeout=30):
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=timeout)
    connect_req = f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n"
    s.sendall(connect_req.encode())
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = s.recv(4096)
        if not chunk:
            raise RuntimeError("proxy closed connection during CONNECT")
        data += chunk
    head, _, _ = data.partition(b"\r\n\r\n")
    if b"200" not in head.split(b"\r\n")[0]:
        raise RuntimeError(f"proxy CONNECT failed: {head!r}")
    return s


def _get_client(timeout=30):
    sock = _open_proxy_socket(REMOTE_HOST, REMOTE_PORT, timeout=timeout)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        REMOTE_HOST,
        port=REMOTE_PORT,
        username=REMOTE_USER,
        password=REMOTE_PASSWORD,
        sock=sock,
        timeout=timeout,
        banner_timeout=timeout,
        auth_timeout=timeout,
        look_for_keys=False,
        allow_agent=False,
    )
    return client


def run_remote(command, timeout=120):
    client = _get_client(timeout=timeout)
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        code = stdout.channel.recv_exit_status()
        return {"code": code, "stdout": out, "stderr": err}
    finally:
        client.close()


def read_remote_file(path):
    client = _get_client()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.open(path, "r") as f:
                return f.read().decode("utf-8", errors="replace")
        finally:
            sftp.close()
    finally:
        client.close()


def write_remote_file(path, content):
    if isinstance(content, str):
        content = content.encode("utf-8")
    client = _get_client()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.open(path, "w") as f:
                f.write(content)
        finally:
            sftp.close()
    finally:
        client.close()


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "echo ok"
    res = run_remote(cmd)
    print(res["stdout"], end="")
    if res["stderr"]:
        print(res["stderr"], end="", file=sys.stderr)
    sys.exit(res["code"])
