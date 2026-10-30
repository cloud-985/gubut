#!/usr/bin/env python3
"""读取服务器 pending-articles.json 前 N 篇候选文章完整内容。"""
import json
import sys
from ssh_tunnel import run_remote

SITE_DIR = "/www/wwwroot/gubut"


def read_candidates(limit=8):
    out, err, code = run_remote("cat %s/pending-articles.json" % SITE_DIR, timeout=60)
    if code != 0:
        print("[ERR] 读取失败:", err, file=sys.stderr)
        return []
    try:
        data = json.loads(out)
    except Exception as e:
        print("[ERR] JSON 解析失败:", e, file=sys.stderr)
        return []
    if not isinstance(data, list):
        return []
    return data[:limit]


if __name__ == "__main__":
    cands = read_candidates()
    print("候选文章数量(前%d): %d" % (8, len(cands)))
    for i, c in enumerate(cands):
        print("\n===== %d =====" % (i + 1))
        print("title:", c.get("title", ""))
        print("link:", c.get("link", ""))
        print("pubDate:", c.get("pubDate", ""))
        print("description:", (c.get("description", "") or "")[:1200])
