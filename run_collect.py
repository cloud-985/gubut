import ssh_tunnel

if __name__ == "__main__":
    out = ssh_tunnel.run_remote("cd /www/wwwroot/gubut && node collect-rss.js")
    print(out)
