"""SSH 隧道助手：通过 HTTP 代理(127.0.0.1:18080)连接生产服务器并执行远程命令/上传文件。"""
import subprocess

HOST = "111.91.30.57"
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY = "127.0.0.1:18080"

_SSH_OPTS = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "ConnectTimeout=20",
    "-o", "ServerAliveInterval=15",
    "-o", f"ProxyCommand=nc -X connect -x {PROXY} %h %p",
]


def _ssh_base():
    return ["sshpass", "-p", PASSWORD, "ssh"] + _SSH_OPTS + [f"{USER}@{HOST}"]


def run_remote(cmd, timeout=180):
    """在远程服务器执行单条命令，返回 (stdout, stderr, returncode)。"""
    proc = subprocess.run(
        _ssh_base() + [cmd],
        capture_output=True, text=True, timeout=timeout,
    )
    return proc.stdout, proc.stderr, proc.returncode


def run_remote_shell(cmd, timeout=180):
    """执行远程命令并返回 stdout+stderr 拼接文本。"""
    out, err, _ = run_remote(cmd, timeout=timeout)
    return (out + err).strip()


def upload(local_path, remote_path, timeout=120):
    """通过代理 scp 上传本地文件到远程。"""
    scp = [
        "sshpass", "-p", PASSWORD, "scp",
    ] + _SSH_OPTS + [local_path, f"{USER}@{HOST}:{remote_path}"]
    proc = subprocess.run(scp, capture_output=True, text=True, timeout=timeout)
    return proc.stdout, proc.stderr, proc.returncode
