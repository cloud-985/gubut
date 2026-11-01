# -*- coding: utf-8 -*-
"""读取服务器端 pending-articles.json 候选文章完整内容, 供 AI 挑选素材。"""
import json

import ssh_tunnel

REMOTE_PENDING = "/www/wwwroot/gubut/pending-articles.json"


def read_pending():
    out, err = ssh_tunnel.run_remote("cat {}".format(REMOTE_PENDING))
    if err.strip():
        print("[read_candidate] stderr:", err.strip()[:500])
    if not out.strip():
        return []
    return json.loads(out)


def main():
    candidates = read_pending()
    print("[read_candidate] 候选文章数量:", len(candidates))
    print("=" * 100)
    for i, a in enumerate(candidates):
        print("[{}] {}".format(i, a.get("title", "")))
        print("    链接: {}".format(a.get("link", "")))
        print("    时间: {}".format(a.get("pubDate", "")))
        print("    摘要: {}".format(a.get("description", "")[:600]))
        print("-" * 100)


if __name__ == "__main__":
    main()
