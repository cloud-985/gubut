import sys
import ssh_tunnel


def main():
    res = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && /usr/bin/node collect-rss.js 2>&1",
        timeout=180,
    )
    sys.stdout.write(res["stdout"])
    if res["stderr"]:
        sys.stderr.write(res["stderr"])
    sys.exit(res["code"])


if __name__ == "__main__":
    main()
