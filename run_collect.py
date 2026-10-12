import ssh_tunnel


def main():
    cmd = f'cd {ssh_tunnel.SITE_DIR} && node collect-rss.js'
    print(ssh_tunnel.run_remote(cmd, timeout=180))


if __name__ == '__main__':
    main()
