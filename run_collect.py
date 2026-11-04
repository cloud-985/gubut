#!/usr/bin/env python3
"""采集 TradingView RSS 候选文章，刷新服务器 pending-articles.json。"""
import sys
from ssh_tunnel import run_remote


def main():
    out, err, code = run_remote("cd /www/wwwroot/gubut && node collect-rss.js", timeout=180)
    sys.stdout.write(out)
    if err.strip():
        sys.stderr.write(err)
    return code


if __name__ == "__main__":
    sys.exit(main() or 0)
