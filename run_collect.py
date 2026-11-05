"""采集 TradingView RSS 候选文章 (在服务器上执行 collect-rss.js)。"""
import ssh_tunnel

CMD = "cd /www/wwwroot/gubut && node collect-rss.js"

if __name__ == "__main__":
    out, err, code = ssh_tunnel.run_remote(CMD, timeout=90)
    print(out, end="")
    if err:
        print("STDERR:", err)
    raise SystemExit(code)
