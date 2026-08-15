#!/usr/bin/env python3
"""read_candidate.py - 读取服务器上 pending-articles.json 前 N 篇候选文章完整内容

用法:
    python3 read_candidate.py [N]   # 默认 N=8
"""
import sys
import json
from ssh_tunnel import ssh_tunnel


def main(n=8):
    raw = ssh_tunnel.get_file("/www/wwwroot/gubut/pending-articles.json")
    data = json.loads(raw)
    print(f"[候选] 共 {len(data)} 篇，读取前 {n} 篇完整内容:\n")
    for i, a in enumerate(data[:n]):
        print("=" * 80)
        print(f"#{i}  pubDate: {a.get('pubDate','')}")
        print(f"标题: {a.get('title','')}")
        print(f"链接: {a.get('link','')}")
        print("描述:")
        print(a.get("description", ""))
        print()
    ssh_tunnel.close()


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    main(n)
