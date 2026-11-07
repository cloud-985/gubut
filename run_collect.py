#!/usr/bin/env python3
"""采集 TradingView RSS 候选文章：调用服务器上的 collect-rss.js 刷新 pending-articles.json。"""
import ssh_tunnel

SITE_DIR = '/www/wwwroot/gubut'


def main():
    r = ssh_tunnel.run_remote(f'cd {SITE_DIR} && node collect-rss.js', timeout=120)
    print(r['stdout'])
    if r['stderr']:
        print(r['stderr'])
    print('exit_code:', r['exit_code'])


if __name__ == '__main__':
    main()
