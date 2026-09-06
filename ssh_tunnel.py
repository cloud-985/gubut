"""
SSH 隧道工具类 - 通过 HTTP 代理建立 SSH 连接
服务器: 111.91.30.57 root 722bza2MtAmwF3Pm
SSH 代理: 127.0.0.1:18080
"""
import paramiko
import socket
import io

SERVER_HOST = '111.91.30.57'
SERVER_USER = 'root'
SERVER_PASS = '722bza2MtAmwF3Pm'
SSH_PROXY_HOST = '127.0.0.1'
SSH_PROXY_PORT = 18080
REMOTE_BASE = '/www/wwwroot/gubut'


class ProxySocket:
    """通过 HTTP CONNECT 代理的 socket 包装，满足 paramiko 接口"""
    def __init__(self):
        self.sock = None
        self._closed = False

    def __call__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30)
        self.sock.connect((SSH_PROXY_HOST, SSH_PROXY_PORT))
        connect_req = f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n"
        self.sock.sendall(connect_req.encode())
        resp = b''
        while b'\r\n\r\n' not in resp:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise Exception("Proxy connection closed")
            resp += chunk
        status_line = resp.split(b'\r\n')[0].decode()
        if '200' not in status_line:
            raise Exception(f"Proxy CONNECT failed: {status_line}")
        return self

    def send(self, data):
        return self.sock.send(data)

    def recv(self, bufsize):
        return self.sock.recv(bufsize)

    def close(self):
        self._closed = True
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

    def settimeout(self, timeout):
        self.sock.settimeout(timeout)

    def fileno(self):
        return self.sock.fileno()

    def getpeername(self):
        return self.sock.getpeername()

    def getsockname(self):
        return self.sock.getsockname()


def get_client():
    """获取 SSH 客户端"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    proxy = ProxySocket()
    client.connect(
        SERVER_HOST,
        port=22,
        username=SERVER_USER,
        password=SERVER_PASS,
        sock=proxy(SERVER_HOST, 22),
        timeout=30,
        banner_timeout=30,
        auth_timeout=30,
    )
    return client


def run_remote(cmd, timeout=120):
    """在远程执行命令，返回 (stdout, stderr, exit_code)"""
    client = get_client()
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        code = stdout.channel.recv_exit_status()
        return out, err, code
    finally:
        client.close()


def remote_read(path):
    """读取远程文件内容"""
    client = get_client()
    try:
        sftp = client.open_sftp()
        with sftp.file(path, 'r') as f:
            content = f.read().decode('utf-8', errors='replace')
        sftp.close()
        return content
    finally:
        client.close()


def remote_write(path, content):
    """写入远程文件"""
    client = get_client()
    try:
        sftp = client.open_sftp()
        with sftp.file(path, 'w') as f:
            f.write(content)
        sftp.close()
        return True
    finally:
        client.close()


def remote_upload(local_path, remote_path):
    """上传文件"""
    client = get_client()
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        return True
    finally:
        client.close()


if __name__ == '__main__':
    print("测试 SSH 连接...")
    out, err, code = run_remote(f"ls -la {REMOTE_BASE}")
    if code == 0:
        print("✓ SSH 连接成功")
        print(out[:800])
    else:
        print(f"✗ SSH 连接失败: {err}")
