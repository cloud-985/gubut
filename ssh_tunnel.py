import subprocess

SSH_HOST = '111.91.30.57'
SSH_PORT = 22
SSH_USER = 'root'
SSH_PASSWORD = '722bza2MtAmwF3Pm'
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 18080
SITE_DIR = '/www/wwwroot/gubut'
SITE_DOMAIN = 'https://www.gubut.com'

PROXY_CMD = f'nc -X connect -x {PROXY_HOST}:{PROXY_PORT} %h %p'


def _base_opts():
    return [
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'ConnectTimeout=20',
        '-o', f'ProxyCommand={PROXY_CMD}',
    ]


def run_remote(cmd, timeout=180):
    full = ['sshpass', '-p', SSH_PASSWORD, 'ssh'] + _base_opts() + [f'{SSH_USER}@{SSH_HOST}', cmd]
    p = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f'SSH 命令执行失败 (exit {p.returncode}): {p.stderr}')
    return p.stdout


def upload(local_path, remote_path, timeout=120):
    full = ['sshpass', '-p', SSH_PASSWORD, 'scp'] + _base_opts() + [local_path, f'{SSH_USER}@{SSH_HOST}:{remote_path}']
    p = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f'SCP 上传失败 (exit {p.returncode}): {p.stderr}')
    return p.stdout


def download(remote_path, local_path, timeout=120):
    full = ['sshpass', '-p', SSH_PASSWORD, 'scp'] + _base_opts() + [f'{SSH_USER}@{SSH_HOST}:{remote_path}', local_path]
    p = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f'SCP 下载失败 (exit {p.returncode}): {p.stderr}')
    return p.stdout
