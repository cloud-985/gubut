# -*- coding: utf-8 -*-
"""采集 TradingView RSS 候选文章并写入服务器 pending-articles.json。"""
import sys

import ssh_tunnel

if __name__ == "__main__":
    out, err, code = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && node collect-rss.js", timeout=180
    )
    print(out)
    if err.strip():
        print(err, file=sys.stderr)
    sys.exit(code)
