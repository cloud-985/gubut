import ssh_tunnel as s

REMOTE_COLLECT = "cd /www/wwwroot/gubut && node collect-rss.js"


def main():
    out, err, code = s.run_remote(REMOTE_COLLECT, timeout=180)
    print(out)
    if err.strip():
        print("STDERR:", err)
    print("exit:", code)
    return code


if __name__ == "__main__":
    main()
