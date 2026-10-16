import json
import sys

sys.path.insert(0, '/workspace')
import ssh_tunnel

REMOTE_DIR = '/www/wwwroot/gubut'


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    data = json.loads(ssh_tunnel.read_file(REMOTE_DIR + '/pending-articles.json'))
    print('候选文章总数:', len(data))
    print()
    for i, a in enumerate(data[:n]):
        print('===== 候选 #{} ====='.format(i + 1))
        print('标题:', a.get('title', ''))
        print('链接:', a.get('link', ''))
        print('发布时间:', a.get('pubDate', ''))
        print('描述:')
        print(a.get('description', ''))
        print()


if __name__ == '__main__':
    main()
