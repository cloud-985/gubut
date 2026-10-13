import sys
import json

from ssh_tunnel import run_remote


def main():
    code, out, err = run_remote(
        "cd /www/wwwroot/gubut && node collect-rss.js", timeout=120
    )
    print(out)
    if err.strip():
        print("STDERR:", err, file=sys.stderr)
    if code != 0:
        print(f"[ERROR] collect-rss.js 退出码 {code}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
