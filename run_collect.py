#!/usr/bin/env python3
"""收集 TradingView RSS 候选文章。

在服务器上运行 collect-rss.js(服务器可直接访问 TradingView),
然后将生成的 pending-articles.json 与去重日志下载到本地,
供后续挑选与改写使用。
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ssh_tunnel

SITE_DIR = "/www/wwwroot/gubut"
LOCAL_PENDING = os.path.join("/workspace", "pending-articles.json")
LOCAL_PUBLISHED = os.path.join("/workspace", ".published-articles.json")


def main():
    print("[1/2] 在服务器上运行 collect-rss.js 采集 TradingView RSS ...")
    out, err, code = ssh_tunnel.run_remote(
        "cd {d} && node collect-rss.js 2>&1".format(d=SITE_DIR),
        timeout=180,
    )
    print(out)
    if err.strip():
        print("[stderr]", err)
    print("[collect-rss 退出码]", code)

    print("[2/2] 下载候选与去重日志到本地 ...")
    out, err, code = ssh_tunnel.run_remote(
        "cat {d}/pending-articles.json".format(d=SITE_DIR), timeout=60
    )
    if code == 0:
        with open(LOCAL_PENDING, "w", encoding="utf-8") as f:
            f.write(out)
        candidates = json.loads(out)
        print("[OK] pending-articles.json 已保存, 候选数:", len(candidates))
        for i, c in enumerate(candidates[:10], 1):
            print("{}. {} | {}".format(i, c.get("title"), c.get("link")))
    else:
        print("[WARN] 读取 pending-articles.json 失败:", err)

    out, err, code = ssh_tunnel.run_remote(
        "cat {d}/.published-articles.json".format(d=SITE_DIR), timeout=60
    )
    if code == 0:
        with open(LOCAL_PUBLISHED, "w", encoding="utf-8") as f:
            f.write(out)
        print("[OK] .published-articles.json 已保存到本地")
    else:
        print("[WARN] 读取 .published-articles.json 失败:", err)


if __name__ == "__main__":
    main()
