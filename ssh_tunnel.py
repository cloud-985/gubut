"""SSH 隧道工具：通过 HTTP CONNECT 代理连接到目标服务器。

环境约定：
- HTTP 代理: 127.0.0.1:18080 (支持 CONNECT 方法)
- 目标服务器: 111.91.30.57:22  root / 722bza2MtAmwF3Pm
- 网站目录: /www/wwwroot/gubut

用法:
    from ssh_tunnel import ssh_tunnel
    out, err, code = ssh_tunnel.run_remote("ls /www/wwwroot/gubut")
    ssh_tunnel.put_remote("/tmp/local.json", "/www/wwwroot/gubut/ai_article.json")
    ssh_tunnel.get_remote("/www/wwwroot/gubut/articles.json", "/tmp/articles.json")
"""
import os
import socket
import paramiko

# 服务器与代理配置
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080
SSH_HOST = "111.91.30.57"
SSH_PORT = 22
SSH_USER = "root"
SSH_PASSWORD = "722bza2MtAmwF3Pm"

REMOTE_ROOT = "/www/wwwroot/gubut"


def _open_tunnel_socket():
    """通过 HTTP CONNECT 代理建立到 SSH 服务器的 TCP 隧道。"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(20)
    sock.connect((PROXY_HOST, PROXY_PORT))
    req = (
        f"CONNECT {SSH_HOST}:{SSH_PORT} HTTP/1.1\r\n"
        f"Host: {SSH_HOST}:{SSH_PORT}\r\n"
        f"Proxy-Connection: keep-alive\r\n\r\n"
    ).encode()
    sock.sendall(req)
    # 读取代理响应
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = sock.recv(4096)
        if not chunk:
            break
        resp += chunk
    head = resp.split(b"\r\n", 1)[0].decode("ascii", "ignore")
    if "200" not in head:
        raise RuntimeError(f"代理 CONNECT 失败: {head}")
    return sock


def _new_ssh_client():
    """新建一个 SSH 客户端（每次调用都建立新连接）。"""
    sock = _open_tunnel_socket()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        SSH_HOST,
        port=SSH_PORT,
        username=SSH_USER,
        password=SSH_PASSWORD,
        sock=sock,
        timeout=20,
        banner_timeout=20,
        auth_timeout=20,
        look_for_keys=False,
        allow_agent=False,
    )
    return client


class _SshTunnel:
    """单例式 SSH 工具封装，便于在脚本里 `ssh_tunnel.run_remote(...)` 调用。"""

    def __init__(self):
        self._client = None

    def _client_get(self):
        if self._client is None or self._closed(self._client):
            self._client = _new_ssh_client()
        return self._client

    @staticmethod
    def _closed(client):
        try:
            transport = client.get_transport()
            return transport is None or not transport.is_active()
        except Exception:
            return True

    def run_remote(self, cmd, timeout=120):
        """在远程执行命令，返回 (stdout, stderr, exit_code)。"""
        client = self._client_get()
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", "ignore")
        err = stderr.read().decode("utf-8", "ignore")
        code = stdout.channel.recv_exit_status()
        return out, err, code

    def put_remote(self, local_path, remote_path):
        """上传本地文件到远程。"""
        client = self._client_get()
        sftp = client.open_sftp()
        try:
            sftp.put(local_path, remote_path)
        finally:
            sftp.close()

    def get_remote(self, remote_path, local_path):
        """从远程下载文件到本地。"""
        client = self._client_get()
        sftp = client.open_sftp()
        try:
            sftp.get(remote_path, local_path)
        finally:
            sftp.close()

    def read_remote(self, remote_path, max_bytes=None):
        """读取远程文件文本内容。"""
        client = self._client_get()
        sftp = client.open_sftp()
        try:
            with sftp.open(remote_path, "r") as fp:
                if max_bytes:
                    data = fp.read(max_bytes)
                else:
                    data = fp.read()
            if isinstance(data, bytes):
                data = data.decode("utf-8", "ignore")
            return data
        finally:
            sftp.close()

    def write_remote(self, remote_path, text):
        """以文本方式覆盖远程文件。"""
        client = self._client_get()
        sftp = client.open_sftp()
        try:
            with sftp.open(remote_path, "w") as fp:
                fp.write(text)
        finally:
            sftp.close()

    def close(self):
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None


ssh_tunnel = _SshTunnel()


if __name__ == "__main__":
    # 自检：打印远程网站目录的前几行
    out, err, code = ssh_tunnel.run_remote(f"ls -la {REMOTE_ROOT} | head -20")
    print("EXIT", code)
    print(out)
    if err.strip():
        print("STDERR:", err)
