"""SSH tunnel utilities for connecting to the remote server through HTTP proxy."""
import socket
import paramiko
import socks

# Server configuration
SSH_HOST = "111.91.30.57"
SSH_PORT = 22
SSH_USER = "root"
SSH_PASS = "722bza2MtAmwF3Pm"

# Proxy configuration
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080

REMOTE_ROOT = "/www/wwwroot/gubut"


def _create_http_connect_tunnel(host, port, proxy_host, proxy_port):
    """Create a socket tunneled through HTTP proxy using CONNECT method."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((proxy_host, proxy_port))

    # Send HTTP CONNECT request
    connect_request = f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n"
    sock.sendall(connect_request.encode())

    # Read response
    response = b""
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk

    response_text = response.decode(errors="ignore")
    if "200" not in response_text.split("\r\n")[0]:
        sock.close()
        raise Exception(f"HTTP CONNECT failed: {response_text.split(chr(10))[0]}")

    return sock


def get_ssh_client():
    """Get a connected SSH client through the proxy."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Try HTTP CONNECT tunnel first
    try:
        sock = _create_http_connect_tunnel(SSH_HOST, SSH_PORT, PROXY_HOST, PROXY_PORT)
        client.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USER,
            password=SSH_PASS,
            sock=sock,
            timeout=30,
            banner_timeout=30,
            auth_timeout=30,
        )
        return client
    except Exception as e:
        print(f"HTTP CONNECT tunnel failed: {e}, trying SOCKS fallback...")

    # Fallback: try SOCKS via PySocks in case proxy supports it
    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.HTTP, addr=PROXY_HOST, port=PROXY_PORT)
        sock.settimeout(30)
        sock.connect((SSH_HOST, SSH_PORT))
        client.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USER,
            password=SSH_PASS,
            sock=sock,
            timeout=30,
            banner_timeout=30,
            auth_timeout=30,
        )
        return client
    except Exception as e2:
        raise Exception(f"All SSH connection methods failed: {e}; {e2}")


def run_remote(cmd):
    """Run a remote command and return stdout as string."""
    client = get_ssh_client()
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        exit_code = stdout.channel.recv_exit_status()
        if exit_code != 0 and err.strip():
            print(f"[run_remote] WARNING stderr ({exit_code}): {err[:500]}")
        return out
    finally:
        client.close()


def read_remote_file(remote_path):
    """Read a remote file content as string."""
    client = get_ssh_client()
    try:
        sftp = client.open_sftp()
        with sftp.file(remote_path, "r") as f:
            data = f.read().decode("utf-8", errors="replace")
        return data
    finally:
        client.close()


def upload_file(local_path, remote_path):
    """Upload a local file to the remote server."""
    client = get_ssh_client()
    try:
        sftp = client.open_sftp()
        # Ensure remote directory exists
        remote_dir = "/".join(remote_path.split("/")[:-1])
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            parent = "/".join(remote_dir.split("/")[:-1])
            try:
                sftp.stat(parent)
                sftp.mkdir(remote_dir)
            except Exception:
                pass
        sftp.put(local_path, remote_path)
    finally:
        client.close()


if __name__ == "__main__":
    # Quick test
    print(run_remote(f"ls -la {REMOTE_ROOT}/pending-articles.json 2>&1; echo '---'; head -c 500 {REMOTE_ROOT}/pending-articles.json 2>&1"))
