#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读取服务器 pending-articles.json 前 N 篇完整内容。"""
import json
import sys
import ssh_tunnel

REMOTE_FILE = "/www/wwwroot/gubut/pending-articles.json"
DEFAULT_LIMIT = 8


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LIMIT
    code, out, err = ssh_tunnel.run_remote("cat %s" % REMOTE_FILE)
    if code != 0:
        print("[读取失败] exit=%s" % code)
        if err:
            print(err)
        return code

    articles = json.loads(out)
    print("候选文章总数: %d" % len(articles))
    print("=" * 70)
    for i, a in enumerate(articles[:n]):
        print("[%d] %s" % (i + 1, a.get("title", "")))
        print("链接: %s" % a.get("link", ""))
        print("发布: %s" % a.get("pubDate", ""))
        print("描述:\n%s" % a.get("description", ""))
        print("=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
