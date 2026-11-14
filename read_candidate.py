#!/usr/bin/env python3
"""读取服务器 pending-articles.json 前 5-8 篇完整内容（供 AI 挑选素材）。"""

import json

import ssh_tunnel

PENDING_REMOTE = "/www/wwwroot/gubut/pending-articles.json"


def main():
    out, err = ssh_tunnel.run_remote("cat " + PENDING_REMOTE)
    if err.strip():
        print("[stderr]", err.strip())
    if not out.strip():
        print("pending-articles.json 为空或不存在")
        return

    data = json.loads(out)
    n = min(8, len(data))
    print("共 %d 篇候选，显示前 %d 篇：\n" % (len(data), n))
    for i, item in enumerate(data[:n], 1):
        print("=" * 72)
        print("[%d] %s" % (i, item.get("title", "")))
        print("链接: %s" % item.get("link", ""))
        print("发布时间: %s" % item.get("pubDate", ""))
        print("描述:\n%s" % item.get("description", ""))
        print()


if __name__ == "__main__":
    main()
