import pexpect
import base64

HOST = "111.91.30.57"
PORT = 22
USER = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def run_remote(command, timeout=120):
    ssh_cmd = (
        "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
        "-o PreferredAuthentications=password -o PubkeyAuthentication=no "
        "-o ConnectTimeout=15 "
        f"-o ProxyCommand='nc -X connect -x {PROXY_HOST}:{PROXY_PORT} %h %p' "
        f"{USER}@{HOST} {command!r}"
    )
    child = pexpect.spawn("/bin/bash", ["-c", ssh_cmd], timeout=timeout, encoding="utf-8")
    child.expect(["assword:", pexpect.EOF, pexpect.TIMEOUT], timeout=timeout)
    if child.after == "assword:":
        child.sendline(PASSWORD)
    child.expect(pexpect.EOF, timeout=timeout)
    output = child.before or ""
    return output


def read_remote_file(path):
    out = run_remote(f"cat {path}")
    lines = out.splitlines()
    if lines and lines[0].strip() == "root@":
        lines = lines[1:]
    return "\n".join(lines)


def write_remote_file(path, content):
    if isinstance(content, str):
        content = content.encode("utf-8")
    b64 = base64.b64encode(content).decode("ascii")
    out = run_remote(f"echo {b64} | base64 -d > {path}")
    return out
