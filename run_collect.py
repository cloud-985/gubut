#!/usr/bin/env python3
"""采集 TradingView RSS 候选文章并刷新服务器 pending-articles.json。

服务器已部署经过验证的 collect-rss.js(直接抓取 TradingView feed 并去重),
这里通过 SSH 触发它, 使 /www/wwwroot/gubut/pending-articles.json 保持最新。
"""
import sys
from ssh_tunnel import run_remote

SITE_DIR = "/www/wwwroot/gubut"


def main():
    print("[采集] 触发服务器 collect-rss.js ...")
    out, err, code = run_remote("cd %s && node collect-rss.js" % SITE_DIR, timeout=180)
    print(out)
    if err.strip():
        print("[stderr]", err, file=sys.stderr)

    # 打印候选数量
    count_cmd = (
        "cd %s && python3 -c \"import json; "
        "d=json.load(open('pending-articles.json')); print('pending count:', len(d))\""
        % SITE_DIR
    )
    out2, err2, code2 = run_remote(count_cmd, timeout=60)
    print(out2)
    if err2.strip():
        print("[stderr]", err2, file=sys.stderr)

    return 0 if code == 0 else code


if __name__ == "__main__":
    sys.exit(main())
