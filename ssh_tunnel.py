import base64
import os
import subprocess

SERVER_HOST = "111.91.30.57"
SERVER_USER = "root"
SERVER_PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = "18080"
SITE_DIR = "/www/wwwroot/gubut"

_ASKPASS_PATH = "/tmp/gubut_askpass.sh"


def _ensure_askpass():
    with open(_ASKPASS_PATH, "w") as f:
        f.write("#!/bin/sh\n")
        f.write("echo '%s'\n" % SERVER_PASSWORD)
    os.chmod(_ASKPASS_PATH, 0o700)
    return _ASKPASS_PATH


def _base_cmd():
    return [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "LogLevel=ERROR",
        "-o", "ConnectTimeout=30",
        "-o", "ServerAliveInterval=15",
        "-o", "ProxyCommand=nc -X connect -x %s:%s %%h %%p" % (PROXY_HOST, PROXY_PORT),
        "%s@%s" % (SERVER_USER, SERVER_HOST),
    ]


def _env():
    env = os.environ.copy()
    env["SSH_ASKPASS"] = _ensure_askpass()
    env["SSH_ASKPASS_REQUIRE"] = "force"
    env["DISPLAY"] = ":0"
    return env


def run_remote(command, timeout=180):
    """在远程服务器执行命令, 返回标准输出文本."""
    cmd = _base_cmd() + [command]
    proc = subprocess.run(
        cmd,
        env=_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    out = proc.stdout.decode("utf-8", "replace")
    if not out.strip():
        out = proc.stderr.decode("utf-8", "replace")
    return out


def upload_text(text, remote_path):
    """将文本写入远程文件(通过 base64 + stdin 传输)."""
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    cmd = _base_cmd() + ["base64 -d > %s" % remote_path]
    proc = subprocess.run(
        cmd,
        env=_env(),
        input=b64.encode("ascii"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=180,
    )
    return proc.stdout.decode("utf-8", "replace")


if __name__ == "__main__":
    import sys

    print(run_remote(sys.argv[1] if len(sys.argv) > 1 else "hostname"))
