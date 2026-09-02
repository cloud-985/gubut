#!/usr/bin/env python3
"""Read top 5-8 pending articles from remote server, print full summary
for AI selection. Usage: python3 read_candidate.py [N] (default 8)."""
import json
import sys
import ssh_tunnel


def main():
    n = 8
    if len(sys.argv) > 1:
        try:
            n = max(1, min(int(sys.argv[1]), 20))
        except ValueError:
            pass

    path = f"{ssh_tunnel.REMOTE_ROOT}/pending-articles.json"
    print(f"📖 读取远程 {path} 前 {n} 篇候选 ...")
    data = ssh_tunnel.read_remote_file(path)
    articles = json.loads(data)
    print(f"   候选总数: {len(articles)}")
    print()

    for i, a in enumerate(articles[:n], start=1):
        print(f"===== [{i}] {(a.get('title') or '')[:100]} =====")
        print(f"  链接: {a.get('link') or ''}")
        print(f"  发布: {a.get('pubDate') or ''}")
        print(f"  描述: {(a.get('description') or '')[:600]}")
        if a.get("content"):
            c = str(a["content"])[:400]
            print(f"  正文片段: {c}")
        print()


if __name__ == "__main__":
    main()
