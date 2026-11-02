#!/usr/bin/env python3
"""SSH helper for gubut.com server access via HTTP CONNECT proxy."""
import pexpect
import shlex

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY = "127.0.0.1:18080"


def _spawn(command):
    cmd = (
        "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
        '-o ProxyCommand="nc -X connect -x %s %%h %%p" '
        "-p %d %s@%s %s"
        % (PROXY, PORT, USER, HOST, shlex.quote(command))
    )
    return pexpect.spawn("/bin/bash", ["-c", cmd], timeout=180, encoding="utf-8")


def run_remote(command, timeout=180):
    """Run a command on the remote server and return stdout (str)."""
    child = _spawn(command)
    child.timeout = timeout
    try:
        i = child.expect(["[Pp]assword:", "Permission denied", pexpect.EOF, pexpect.TIMEOUT])
        if i == 0:
            child.sendline(PASSWORD)
        child.expect(pexpect.EOF)
        out = child.before or ""
    finally:
        child.close()
    # Strip the SSH password prompt echo / banner noise
    out = out.replace("Password:", "").strip("\r\n")
    return out


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "hostname"
    print(run_remote(cmd))
