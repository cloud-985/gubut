import socket
import paramiko

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASS = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def get_sock():
    s = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=20)
    s.sendall(
        (
            f"CONNECT {HOST}:{PORT} HTTP/1.1\r\n"
            f"Host: {HOST}:{PORT}\r\n"
            "Proxy-Connection: Keep-Alive\r\n\r\n"
        ).encode()
    )
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            break
        resp += chunk
    if b"200" not in resp.split(b"\r\n")[0]:
        raise RuntimeError("proxy CONNECT failed")
    return s


def run_remote(cmd):
    sock = get_sock()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        HOST, port=PORT, username=USER, password=PASS, sock=sock,
        timeout=20, banner_timeout=20, auth_timeout=20,
        look_for_keys=False, allow_agent=False,
    )
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    client.close()
    sock.close()
    return out, err


def read_remote(path):
    out, err = run_remote(f"cat {path}")
    return out, err


def sftp_put(local_path, remote_path):
    sock = get_sock()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        HOST, port=PORT, username=USER, password=PASS, sock=sock,
        timeout=20, banner_timeout=20, auth_timeout=20,
        look_for_keys=False, allow_agent=False,
    )
    sftp = client.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    client.close()
    sock.close()
    return remote_path


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        out, err = read_remote(p)
        print(f"===== {p} =====")
        print(out)
        if err:
            print(f"--- STDERR ---\n{err}")
