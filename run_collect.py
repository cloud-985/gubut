#!/usr/bin/env python3
"""采集 TradingView RSS 候选文章：在服务器上运行 collect-rss.js。"""
import ssh_tunnel as s

CMD = "cd /www/wwwroot/gubut && node collect-rss.js"

if __name__ == "__main__":
    out, err, code = s.run_remote(CMD, timeout=120)
    print(out)
    if err:
        print("STDERR:", err)
    print("EXIT:", code)
