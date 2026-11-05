"""SSH tunnel helper for gubut.com server.

Routes SSH through the HTTP CONNECT proxy at 127.0.0.1:18080 using paramiko.
"""
import socket
import paramiko

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def _connect_socket(timeout=30):
    """Establish an HTTP CONNECT tunnel to the target SSH host."""
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=timeout)
    req = f"CONNECT {HOST}:{PORT} HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n\r\n"
    s.sendall(req.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            break
        resp += chunk
    if not resp.startswith(b"HTTP/1.1 200"):
        raise ConnectionError(f"Proxy CONNECT failed: {resp.splitlines()[0] if resp else b'no response'}")
    return s


def _client(timeout=30):
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sock = _connect_socket(timeout)
    cli.connect(
        HOST,
        port=PORT,
        username=USER,
        password=PASSWORD,
        timeout=timeout,
        sock=sock,
        look_for_keys=False,
        allow_agent=False,
    )
    return cli


def run_remote(command, timeout=60):
    """Run a shell command on the server and return (stdout, stderr, exit_code)."""
    cli = _client(timeout)
    try:
        stdin, stdout, stderr = cli.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        code = stdout.channel.recv_exit_status()
        return out, err, code
    finally:
        cli.close()


def put_file(local_path, remote_path):
    """Upload a local file to the server via SFTP."""
    cli = _client(60)
    try:
        sftp = cli.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        return True
    finally:
        cli.close()


def get_file(remote_path, local_path):
    """Download a file from the server via SFTP."""
    cli = _client(60)
    try:
        sftp = cli.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        return True
    finally:
        cli.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        out, err, code = run_remote(sys.argv[1])
        print(out, end="")
        if err:
            print("STDERR:", err, file=sys.stderr)
        sys.exit(code)
