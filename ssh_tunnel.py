import paramiko
import json
import os

SSH_HOST = '111.91.30.57'
SSH_PORT = 22
SSH_USER = 'root'
SSH_PASS = '722bza2MtAmwF3Pm'
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 18080
REMOTE_BASE = '/www/wwwroot/gubut'


def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS,
            timeout=30, allow_agent=False, look_for_keys=False
        )
    except Exception:
        client.connect(
            SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS,
            timeout=30, allow_agent=False, look_for_keys=False,
            sock=paramiko.ProxyCommand(f'nc -x {PROXY_HOST}:{PROXY_PORT} %h %p')
        )
    return client


def run_remote(cmd, timeout=300):
    client = get_ssh_client()
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        return {'exit_code': exit_code, 'stdout': out, 'stderr': err}
    finally:
        client.close()


def run_remote_python(script_content):
    return run_remote(f"python3 -c {json.dumps(script_content)}")


def read_remote_file(filepath):
    return run_remote(f'cat {filepath}')


def write_remote_file(filepath, content):
    import base64
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    return run_remote(f"echo '{encoded}' | base64 -d > {filepath}")


def append_to_articles_json(article_data):
    import base64
    encoded = base64.b64encode(json.dumps(article_data, ensure_ascii=False).encode('utf-8')).decode('ascii')
    script = f"""
import json, os
path = '{REMOTE_BASE}/articles.json'
data = json.loads(os.popen('cat ' + path).read() or '[]')
new_item = json.loads(base64.b64decode('{encoded}').decode('utf-8'))
data.insert(0, new_item)
os.popen(f"echo '{{}}' > {path}").write(json.dumps(data, ensure_ascii=False, indent=2))
"""
    return run_remote_python(script)


def get_remote_articles():
    result = read_remote_file(f'{REMOTE_BASE}/articles.json')
    if result['exit_code'] != 0:
        return []
    return json.loads(result['stdout'])
