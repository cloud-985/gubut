"""
SSH隧道工具 - 通过代理连接远程服务器并执行命令/传输文件
"""
import paramiko
import os
from typing import Optional, Tuple

# 服务器配置
SERVER_HOST = "111.91.30.57"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASS = "722bza2MtAmwF3Pm"
SERVER_WEB_DIR = "/www/wwwroot/gubut"

# 代理配置
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 18080


def create_ssh_client() -> paramiko.SSHClient:
    """创建SSH客户端连接（通过代理）"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 尝试通过代理连接，如果失败则直连
    try:
        # 使用socks代理
        import socket
        try:
            import socks
            proxy = socks.socksocket()
            proxy.set_proxy(socks.SOCKS5, PROXY_HOST, PROXY_PORT)
            proxy.connect((SERVER_HOST, SERVER_PORT))
            transport = paramiko.Transport(proxy)
            transport.connect(username=SERVER_USER, password=SERVER_PASS)
            ssh._transport = transport
            print(f"[SSH] 已通过代理 {PROXY_HOST}:{PROXY_PORT} 连接到 {SERVER_HOST}")
            return ssh
        except ImportError:
            # 没有socks库，尝试直连
            pass
    except Exception as e:
        print(f"[SSH] 代理连接失败: {e}，尝试直连...")

    # 直连方式
    ssh.connect(
        hostname=SERVER_HOST,
        port=SERVER_PORT,
        username=SERVER_USER,
        password=SERVER_PASS,
        timeout=30,
        banner_timeout=30,
        auth_timeout=30
    )
    print(f"[SSH] 已直连到 {SERVER_HOST}")
    return ssh


def run_remote(command: str, timeout: int = 60) -> Tuple[int, str, str]:
    """
    在远程服务器上执行命令
    
    Args:
        command: 要执行的shell命令
        timeout: 超时时间（秒）
    
    Returns:
        (exit_code, stdout, stderr)
    """
    ssh = None
    try:
        ssh = create_ssh_client()
        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        return exit_code, out, err
    except Exception as e:
        return -1, "", str(e)
    finally:
        if ssh:
            try:
                ssh.close()
            except:
                pass


def upload_file(local_path: str, remote_path: str) -> bool:
    """
    上传文件到远程服务器
    
    Args:
        local_path: 本地文件路径
        remote_path: 远程文件路径
    
    Returns:
        是否成功
    """
    ssh = None
    try:
        ssh = create_ssh_client()
        sftp = ssh.open_sftp()
        # 确保远程目录存在
        remote_dir = os.path.dirname(remote_path)
        if remote_dir:
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                # 尝试创建目录
                run_remote(f"mkdir -p {remote_dir}")
        sftp.put(local_path, remote_path)
        sftp.close()
        print(f"[SCP] 已上传 {local_path} -> {remote_path}")
        return True
    except Exception as e:
        print(f"[SCP] 上传失败: {e}")
        return False
    finally:
        if ssh:
            try:
                ssh.close()
            except:
                pass


def download_file(remote_path: str, local_path: str) -> bool:
    """
    从远程服务器下载文件
    
    Args:
        remote_path: 远程文件路径
        local_path: 本地保存路径
    
    Returns:
        是否成功
    """
    ssh = None
    try:
        ssh = create_ssh_client()
        sftp = ssh.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        print(f"[SCP] 已下载 {remote_path} -> {local_path}")
        return True
    except Exception as e:
        print(f"[SCP] 下载失败: {e}")
        return False
    finally:
        if ssh:
            try:
                ssh.close()
            except:
                pass


if __name__ == "__main__":
    # 测试连接
    code, out, err = run_remote("echo '连接成功' && hostname && pwd")
    print(f"Exit: {code}")
    print(f"Stdout: {out}")
    print(f"Stderr: {err}")
