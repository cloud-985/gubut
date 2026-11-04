#!/usr/bin/env python3
"""读取服务器 pending-articles.json 前 N 篇候选的完整内容。"""
import json
import sys

from ssh_tunnel import run_remote


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    out, err, code = run_remote("cat /www/wwwroot/gubut/pending-articles.json", timeout=120)
    if code != 0:
        sys.stderr.write(err or out)
        return code
    items = json.loads(out)
    print(f"共 {len(items)} 篇候选\n")
    for i, it in enumerate(items[:n]):
        print(f"===== 候选 {i + 1} =====")
        print("标题:", it.get("title"))
        print("链接:", it.get("link"))
        print("发布时间:", it.get("pubDate"))
        print("描述:", it.get("description"))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
