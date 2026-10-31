#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过 HTTP CONNECT 代理 SSH 到 gubut 服务器并执行远程命令。"""
import pexpect
import sys

HOST = "111.91.30.57"
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY = "127.0.0.1:18080"
SSH_OPTS = (
    "-o StrictHostKeyChecking=no "
    "-o UserKnownHostsFile=/dev/null "
    f'-o ProxyCommand="nc -X connect -x {PROXY} %h %p"'
)


def run_remote(command, timeout=60):
    """执行远程命令并返回 stdout 字符串（不含密码提示行）。"""
    remote = command.replace('"', '\\"')
    cmd = f'ssh {SSH_OPTS} {USER}@{HOST} "{remote}"'
    child = pexpect.spawn(cmd, timeout=timeout, encoding="utf-8")
    i = child.expect(["password:", "Password:", pexpect.EOF, pexpect.TIMEOUT])
    if i in (0, 1):
        child.sendline(PASSWORD)
    out = child.read()
    child.close()
    # 去掉 ssh 的警告行与密码回显行
    lines = []
    skip_next = False
    for line in out.splitlines():
        if skip_next:
            skip_next = False
            continue
        if "Permanently added" in line or "password:" in line.lower():
            if "password:" in line.lower():
                skip_next = True
            continue
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    print(run_remote(sys.argv[1] if len(sys.argv) > 1 else "echo ok"))
