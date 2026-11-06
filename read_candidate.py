# -*- coding: utf-8 -*-
"""读取服务器 pending-articles.json 中前 N 篇候选的完整内容。"""
import json
import sys

import ssh_tunnel


def load_candidates():
    raw = ssh_tunnel.read_file("/www/wwwroot/gubut/pending-articles.json")
    return json.loads(raw)


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    candidates = load_candidates()
    print("候选总数: {}".format(len(candidates)))
    for i, c in enumerate(candidates[:limit]):
        print("\n" + "=" * 70)
        print("[{}] {}".format(i + 1, c.get("title", "")))
        print("链接: {}".format(c.get("link", "")))
        print("发布时间: {}".format(c.get("pubDate", "")))
        print("-" * 70)
        print(c.get("description", ""))


if __name__ == "__main__":
    main()
