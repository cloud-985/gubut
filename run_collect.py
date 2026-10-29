#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""采集 TradingView RSS 候选文章：在服务器上运行 collect-rss.js 刷新 pending-articles.json。"""
import ssh_tunnel

CMD = "cd /www/wwwroot/gubut && node collect-rss.js"


def main():
    print("[采集] 正在远程执行 collect-rss.js ...")
    code, out, err = ssh_tunnel.run_remote(CMD)
    print("exit=%s" % code)
    if out:
        print(out)
    if err:
        print("[stderr]\n%s" % err)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
