#!/usr/bin/env python3
"""run_collect.py - 触发服务器端 RSS 采集，刷新 pending-articles.json

用法:
    cd /workspace && python3 run_collect.py
"""
import sys
from ssh_tunnel import ssh_tunnel


def main():
    print("[采集] 通过 SSH 触发服务器端 RSS 采集 ...")
    cmd = "cd /www/wwwroot/gubut && node collect-rss.js 2>&1"
    rc, out, err = ssh_tunnel.run_remote(cmd, timeout=120)
    print(out)
    if err:
        print("[STDERR]", err, file=sys.stderr)
    if rc != 0:
        print(f"[采集] 服务器执行失败 rc={rc}", file=sys.stderr)
        sys.exit(rc)

    # 统计候选数量
    rc2, out2, _ = ssh_tunnel.run_remote(
        'python3 -c \'import json; d=json.load(open("/www/wwwroot/gubut/pending-articles.json")); print("候选文章数:", len(d))\''
    )
    print(out2)
    ssh_tunnel.close()


if __name__ == "__main__":
    main()
