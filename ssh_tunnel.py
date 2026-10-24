import socket

import paramiko

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080

SSH_HOST = "111.91.30.57"
SSH_PORT = 22
SSH_USER = "root"
SSH_PASSWORD = "722bza2MtAmwF3Pm"

REMOTE_DIR = "/www/wwwroot/gubut"


def _proxy_socket(host, port, timeout=30):
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=timeout)
    req = "CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n".format(
        host=host, port=port
    )
    s.sendall(req.encode("ascii"))
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            break
        resp += chunk
    status_line = resp.split(b"\r\n", 1)[0]
    if b"200" not in status_line:
        s.close()
        raise RuntimeError("proxy CONNECT failed: {!r}".format(resp[:300]))
    return s


def get_client(timeout=30):
    sock = _proxy_socket(SSH_HOST, SSH_PORT, timeout)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        SSH_HOST,
        port=SSH_PORT,
        username=SSH_USER,
        password=SSH_PASSWORD,
        sock=sock,
        timeout=timeout,
        look_for_keys=False,
        allow_agent=False,
        banner_timeout=timeout,
        auth_timeout=timeout,
    )
    return client


def run_remote(command, timeout=120):
    client = get_client(timeout=timeout)
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        code = stdout.channel.recv_exit_status()
        return {"code": code, "stdout": out, "stderr": err}
    finally:
        client.close()


def run_remote_file(command, timeout=120):
    client = get_client(timeout=timeout)
    try:
        transport = client.get_transport()
        sftp = paramiko.SFTPClient.from_transport(transport)
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        code = stdout.channel.recv_exit_status()
        return {"code": code, "stdout": out, "stderr": err, "sftp": sftp, "transport": transport}
    except Exception:
        client.close()
        raise


def upload_file(local_path, remote_path):
    client = get_client(timeout=60)
    try:
        transport = client.get_transport()
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        client.close()


def download_file(remote_path, local_path):
    client = get_client(timeout=60)
    try:
        transport = client.get_transport()
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_path, local_path)
        sftp.close()
    finally:
        client.close()


if __name__ == "__main__":
    result = run_remote("echo OK && hostname && pwd && ls {}".format(REMOTE_DIR))
    print("code:", result["code"])
    print("stdout:", result["stdout"])
    if result["stderr"]:
        print("stderr:", result["stderr"])
