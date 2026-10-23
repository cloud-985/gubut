# -*- coding: utf-8 -*-
"""读取服务器 pending-articles.json 前若干篇候选文章完整内容。"""
import json
import sys

import ssh_tunnel


def read_candidates(limit=8):
    out, err, code = ssh_tunnel.run_remote(
        "cat /www/wwwroot/gubut/pending-articles.json", timeout=60
    )
    if code != 0 or not out.strip():
        print("读取 pending-articles.json 失败:", err or "空内容", file=sys.stderr)
        return []
    data = json.loads(out)
    return data[:limit]


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    candidates = read_candidates(limit)
    print(f"共返回 {len(candidates)} 篇候选：")
    for i, c in enumerate(candidates, 1):
        print(f"\n===== 候选 {i} =====")
        print("标题:", c.get("title"))
        print("链接:", c.get("link"))
        print("发布日期:", c.get("pubDate"))
        print("描述:", c.get("description"))
