"""
SSH隧道工具 - 通过本地代理连接远程服务器
服务器: 111.91.30.57 root 722bza2MtAmwF3Pm
代理: 127.0.0.1:18080
"""
import paramiko
import socks
import socket
import json
import os

SERVER_HOST = "111.91.30.57"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASS = "722bza2MtAmwF3Pm"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080
REMOTE_DIR = "/www/wwwroot/gubut"


def create_ssh_client():
    """创建通过代理的SSH客户端连接"""
    # 创建socket代理
    sock = socks.socksocket()
    sock.set_proxy(
        proxy_type=socks.SOCKS5,
        addr=PROXY_HOST,
        port=PROXY_PORT
    )
    sock.connect((SERVER_HOST, SERVER_PORT))
    
    # 创建SSH客户端
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=SERVER_HOST,
        port=SERVER_PORT,
        username=SERVER_USER,
        password=SERVER_PASS,
        sock=sock,
        timeout=30
    )
    return client


def run_remote(command):
    """在远程服务器上执行命令并返回输出"""
    client = None
    try:
        client = create_ssh_client()
        stdin, stdout, stderr = client.exec_command(command, timeout=60)
        output = stdout.read().decode("utf-8", errors="replace")
        error = stderr.read().decode("utf-8", errors="replace")
        return output + error
    except Exception as e:
        return f"ERROR: {str(e)}"
    finally:
        if client:
            try:
                client.close()
            except:
                pass


def read_remote_file(remote_path):
    """读取远程服务器文件内容"""
    return run_remote(f"cat {remote_path}")


def write_remote_file(remote_path, content):
    """写入内容到远程服务器文件"""
    # 使用base64编码避免特殊字符问题
    import base64
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    return run_remote(f'echo "{encoded}" | base64 -d > {remote_path}')


def sftp_upload(local_path, remote_path):
    """通过SFTP上传文件到远程服务器"""
    client = None
    try:
        client = create_ssh_client()
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        return "OK"
    except Exception as e:
        return f"ERROR: {str(e)}"
    finally:
        if client:
            try:
                client.close()
            except:
                pass


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        print(run_remote(cmd))
    else:
        print("测试连接...")
        result = run_remote("ls /www/wwwroot/gubut | head -20")
        print(result)
