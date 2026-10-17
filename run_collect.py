import ssh_tunnel

if __name__ == "__main__":
    code, out, err = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && node collect-rss.js"
    )
    print(out)
    if err.strip():
        print("STDERR:", err)
    raise SystemExit(code)
