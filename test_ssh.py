import socket
import paramiko

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASS = "722bza2MtAmwF3Pm"


def connect_via_proxy(proxy_host="127.0.0.1", proxy_port=18080):
    s = socket.create_connection((proxy_host, proxy_port), timeout=15)
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
    print("PROXY RESPONSE:", resp.split(b"\r\n")[0])
    if b"200" not in resp.split(b"\r\n")[0]:
        raise RuntimeError("proxy CONNECT failed: " + resp.decode(errors="replace"))
    return s


def try_connect(desc, transport_sock):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            HOST,
            port=PORT,
            username=USER,
            password=PASS,
            sock=transport_sock,
            timeout=15,
            banner_timeout=15,
            auth_timeout=15,
            look_for_keys=False,
            allow_agent=False,
        )
        print(f"[OK] {desc}: connected")
        stdin, stdout, stderr = client.exec_command(
            "ls -la /www/wwwroot/gubut | head -50"
        )
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        print("--- ls output ---")
        print(out)
        if err:
            print("--- stderr ---")
            print(err)
        client.close()
        return True
    except Exception as e:
        print(f"[FAIL] {desc}: {type(e).__name__}: {e}")
        return False


# Direct
try:
    try_connect("direct", None)
except Exception as e:
    print("direct exception:", e)

# Via proxy
try:
    sock = connect_via_proxy()
    try_connect("via proxy", sock)
    sock.close()
except Exception as e:
    print("proxy exception:", type(e).__name__, e)
