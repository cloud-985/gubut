import sys

sys.path.insert(0, '/workspace')
import ssh_tunnel

REMOTE_DIR = '/www/wwwroot/gubut'


def main():
    print('[发布] 上传 ai_article.json 到服务器...')
    ssh_tunnel.put_file('/workspace/ai_article.json', REMOTE_DIR + '/ai_article.json')
    print('[发布] 已上传 ai_article.json')

    print('[发布] 执行服务器端 _publish_ai.js ...')
    out, err = ssh_tunnel.run_remote('cd {} && node _publish_ai.js'.format(REMOTE_DIR), timeout=180)
    print(out)
    if err.strip():
        print('[STDERR]')
        print(err)


if __name__ == '__main__':
    main()
