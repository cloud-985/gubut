import sys
sys.path.insert(0, '.')
from ssh_tunnel import run_remote, REMOTE_DIR, read_remote_json
print('Testing SSH connection via SOCKS5 proxy...')
result = run_remote(f'ls -la {REMOTE_DIR}/pending-articles.json 2>&1')
print(result)
print('---')
try:
    d = read_remote_json(f'{REMOTE_DIR}/pending-articles.json')
    print(f"pending articles count: {len(d)}")
    for i, a in enumerate(d[:10]):
        title = a.get("title","")[:70]
        asset = a.get("asset","?")
        full_len = len(a.get("full_content",""))
        print(f"  [{i+1}] [{asset}] {title} (full:{full_len})")
except Exception as e:
    print(f"read_remote_json error: {e}")
    # fallback: list dir
    result = run_remote(f'ls -la {REMOTE_DIR}/ | head -30')
    print(result)
