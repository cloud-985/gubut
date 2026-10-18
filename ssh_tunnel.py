import socket
import paramiko

SERVER_HOST = "111.91.30.57"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def _proxy_socket():
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=30)
    req = (
        "CONNECT {host}:{port} HTTP/1.1\r\n"
        "Host: {host}:{port}\r\n\r\n"
    ).format(host=SERVER_HOST, port=SERVER_PORT).encode()
    s.sendall(req)
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            break
        resp += chunk
    status_line = resp.split(b"\r\n", 1)[0]
    if b"200" not in status_line:
        s.close()
        raise RuntimeError("代理 CONNECT 失败: " + status_line.decode(errors="replace"))
    return s


def _connect():
    sock = _proxy_socket()
    transport = paramiko.Transport(sock)
    transport.connect(username=SERVER_USER, password=SERVER_PASSWORD)
    return transport


def run_remote(command, timeout=120):
    transport = _connect()
    try:
        chan = transport.open_session()
        chan.settimeout(timeout)
        chan.exec_command(command)
        out = b""
        err = b""
        while True:
            if chan.recv_ready():
                out += chan.recv(65536)
            if chan.recv_stderr_ready():
                err += chan.recv_stderr(65536)
            if chan.exit_status_ready():
                break
        while chan.recv_ready():
            out += chan.recv(65536)
        while chan.recv_stderr_ready():
            err += chan.recv_stderr(65536)
        code = chan.recv_exit_status()
        return {
            "stdout": out.decode("utf-8", errors="replace"),
            "stderr": err.decode("utf-8", errors="replace"),
            "code": code,
        }
    finally:
        transport.close()


def upload_file(local_path, remote_path):
    transport = _connect()
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        transport.close()


def download_file(remote_path, local_path):
    transport = _connect()
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_path, local_path)
        sftp.close()
    finally:
        transport.close()


if __name__ == "__main__":
    import sys
    result = run_remote(" ".join(sys.argv[1:]))
    print(result["stdout"], end="")
    if result["stderr"]:
        print(result["stderr"], file=sys.stderr, end="")
    sys.exit(result["code"])
