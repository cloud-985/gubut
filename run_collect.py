import json
import sys

sys.path.insert(0, '/workspace')
import ssh_tunnel

REMOTE_DIR = '/www/wwwroot/gubut'


def main():
    print('[采集] 通过 SSH 调用服务器 collect-rss.js 采集 TradingView RSS...')
    out, err = ssh_tunnel.run_remote('cd {} && node collect-rss.js'.format(REMOTE_DIR), timeout=180)
    print(out)
    if err.strip():
        print('[STDERR]')
        print(err)

    try:
        data = json.loads(ssh_tunnel.read_file(REMOTE_DIR + '/pending-articles.json'))
        print('[采集] 候选文章总数:', len(data))
    except Exception as e:
        print('[采集] 读取 pending-articles.json 失败:', e)


if __name__ == '__main__':
    main()
