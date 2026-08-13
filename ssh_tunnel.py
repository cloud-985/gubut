import subprocess
import json
import os

# 服务器配置
HOST = "111.91.30.57"
PORT = 22
USERNAME = "root"
PASSWORD = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080

REMOTE_DIR = "/www/wwwroot/gubut"

# SSH公共选项
SSH_OPTS = [
    "-o", f"ProxyCommand=nc -X connect -x {PROXY_HOST}:{PROXY_PORT} %h %p",
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "ConnectTimeout=20",
    "-o", "PreferredAuthentications=password",
    "-o", "PubkeyAuthentication=no",
    "-o", "LogLevel=ERROR",
    f"-p{PORT}",
]


def run_remote(command, timeout=120):
    """通过sshpass+HTTP CONNECT远程执行命令并返回输出"""
    ssh_cmd = [
        "sshpass", "-p", PASSWORD,
        "ssh", *SSH_OPTS,
        f"{USERNAME}@{HOST}",
        command
    ]
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.stderr:
            # 过滤掉常见警告
            stderr_filtered = "\n".join(
                line for line in result.stderr.split("\n")
                if "Warning" not in line and "Permanently added" not in line and line.strip()
            )
            if stderr_filtered.strip():
                print(f"[SSH stderr] {stderr_filtered[:300]}")
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"SSH命令超时 ({timeout}s): {command[:50]}...")
        return ""
    except Exception as e:
        print(f"SSH执行失败: {e}")
        return ""


def upload_file(local_path, remote_path, timeout=120):
    """通过sshpass+SCP上传文件到远程服务器"""
    scp_cmd = [
        "sshpass", "-p", PASSWORD,
        "scp", *SSH_OPTS,
        "-O",  # 使用legacy SCP协议，兼容性更好
        local_path,
        f"{USERNAME}@{HOST}:{remote_path}"
    ]
    try:
        result = subprocess.run(
            scp_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            print(f"[SCP上传] {local_path} -> {remote_path}")
            return True
        else:
            print(f"[SCP上传失败] {result.stderr[:300]}")
            # 尝试用SFTP方式
            print("尝试用SFTP方式上传...")
            return upload_file_sftp(local_path, remote_path, timeout)
    except subprocess.TimeoutExpired:
        print(f"SCP上传超时: {local_path}")
        return False
    except Exception as e:
        print(f"SCP上传异常: {e}")
        return False


def upload_file_sftp(local_path, remote_path, timeout=120):
    """通过sftp命令上传（备选方案）"""
    # 构造包含代理的sftp命令
    sftp_cmd = [
        "sshpass", "-p", PASSWORD,
        "sftp",
        "-o", f"ProxyCommand=nc -X connect -x {PROXY_HOST}:{PROXY_PORT} %h %p",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=20",
        "-o", "PreferredAuthentications=password",
        "-o", "PubkeyAuthentication=no",
        "-o", "LogLevel=ERROR",
        f"-P{PORT}",
    ]
    
    # 用管道发送put命令
    try:
        input_text = f"put {local_path} {remote_path}\nbye\n"
        result = subprocess.run(
            sftp_cmd + [f"{USERNAME}@{HOST}"],
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            print(f"[SFTP上传] {local_path} -> {remote_path}")
            return True
        else:
            print(f"[SFTP上传失败] stderr: {result.stderr[:300]}")
            print(f"[SFTP上传失败] stdout: {result.stdout[:300]}")
            return False
    except Exception as e:
        print(f"SFTP上传异常: {e}")
        return False


def download_file(remote_path, local_path, timeout=120):
    """通过SCP从远程服务器下载文件"""
    scp_cmd = [
        "sshpass", "-p", PASSWORD,
        "scp", *SSH_OPTS,
        "-O",
        f"{USERNAME}@{HOST}:{remote_path}",
        local_path
    ]
    try:
        result = subprocess.run(
            scp_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            print(f"[SCP下载] {remote_path} -> {local_path}")
            return True
        else:
            print(f"[SCP下载失败] {result.stderr[:300]}")
            return False
    except Exception as e:
        print(f"SCP下载异常: {e}")
        return False


def read_remote_json(remote_path):
    """读取远程JSON文件"""
    content = run_remote(f"cat {remote_path}")
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"内容前500字符: {content[:500]}")
        return None


if __name__ == "__main__":
    # 测试连接
    print("测试SSH连接...")
    result = run_remote("echo '连接成功!'; ls -la /www/wwwroot/gubut/ | head -15")
    print(result)
