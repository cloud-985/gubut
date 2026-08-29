import sys, os, json
sys.path.insert(0, '.')
from ssh_tunnel import REMOTE_DIR, read_remote_json

d = read_remote_json(f'{REMOTE_DIR}/pending-articles.json')
print(f"Total pending: {len(d)}")
# Show all with details
for i, a in enumerate(d):
    title = a.get("title","")[:100]
    asset = a.get("asset","?")
    link = a.get("link","")[:100]
    summary = a.get("summary","")
    full = a.get("full_content","")
    summary_len = len(summary)
    full_len = len(full)
    keys_count = len(a.keys())
    print(f"\n[{i+1}] [{asset:8s}] {title}")
    print(f"    link: {link}")
    print(f"    summary:{summary_len}  full:{full_len}  keys:{list(a.keys())}")
    if summary:
        print(f"    ---摘要前400字---")
        print(summary[:400])
    if full and full_len > 200:
        print(f"    ---全文前600字---")
        print(full[:600])
