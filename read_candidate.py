#!/usr/bin/env python3
"""读取服务器 pending-articles.json 候选文章完整内容。"""
import json
import sys
import ssh_tunnel

REMOTE_PATH = "/www/wwwroot/gubut/pending-articles.json"


def main():
    raw = ssh_tunnel.get_file_bytes(REMOTE_PATH)
    candidates = json.loads(raw.decode("utf-8"))
    print(f"候选文章总数: {len(candidates)}\n")
    n = 8
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    for i, c in enumerate(candidates[:n]):
        print("=" * 70)
        print(f"[{i}] {c.get('title', '')}")
        print(f"    链接: {c.get('link', '')}")
        print(f"    时间: {c.get('pubDate', '')}")
        desc = c.get("description", "")
        print(f"    摘要: {desc}")
        print()


if __name__ == "__main__":
    main()
