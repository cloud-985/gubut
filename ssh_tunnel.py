#!/usr/bin/env python3
"""SSH 隧道辅助模块: 通过本地 HTTP 代理连接 gubut.com 服务器并执行远程命令。"""
import os
import subprocess

HOST = "111.91.30.57"
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY = "127.0.0.1:18080"
ASKPASS_PATH = "/tmp/gubut_askpass.sh"


def _ensure_askpass():
    if not os.path.exists(ASKPASS_PATH):
        with open(ASKPASS_PATH, "w") as f:
            f.write("#!/bin/sh\necho %s\n" % PASSWORD)
        os.chmod(ASKPASS_PATH, 0o700)


def run_remote(command, timeout=120):
    """在远程服务器执行命令, 返回 (stdout, stderr, exit_code)。"""
    _ensure_askpass()
    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    env["SSH_ASKPASS"] = ASKPASS_PATH
    env["SSH_ASKPASS_REQUIRE"] = "force"
    cmd = [
        "setsid", "-w", "ssh",
        "-o", "ConnectTimeout=20",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ProxyCommand=nc -X connect -x %s %%h %%p" % PROXY,
        "%s@%s" % (USER, HOST),
        command,
    ]
    p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)
    return p.stdout, p.stderr, p.returncode


if __name__ == "__main__":
    out, err, code = run_remote("echo CONNECTED && hostname && whoami")
    print("=== stdout ===")
    print(out)
    if err.strip():
        print("=== stderr ===")
        print(err)
    print("exit_code:", code)
