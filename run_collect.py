import sys

sys.path.insert(0, "/workspace")
import ssh_tunnel


def main():
    print("[采集] 正在服务器执行 TradingView RSS 采集...")
    out, err = ssh_tunnel.run_remote("cd /www/wwwroot/gubut && node collect-rss.js")
    print(out)
    if err:
        print("--- STDERR ---")
        print(err)


if __name__ == "__main__":
    main()
