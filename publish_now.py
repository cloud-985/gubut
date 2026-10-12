import json
import os

import ssh_tunnel

LOCAL_ARTICLE = '/workspace/ai_article.json'
REMOTE_ARTICLE = f'{ssh_tunnel.SITE_DIR}/ai_article.json'


def main():
    if not os.path.exists(LOCAL_ARTICLE):
        raise RuntimeError(f'{LOCAL_ARTICLE} 不存在，请先运行 gen_article.py')

    with open(LOCAL_ARTICLE, 'r', encoding='utf-8') as f:
        article = json.load(f)

    print(f"上传 {LOCAL_ARTICLE} -> {REMOTE_ARTICLE}")
    ssh_tunnel.upload(LOCAL_ARTICLE, REMOTE_ARTICLE)
    print('上传完成')

    print('执行远程发布任务 _publish_ai.js ...')
    out = ssh_tunnel.run_remote(f'cd {ssh_tunnel.SITE_DIR} && node _publish_ai.js', timeout=180)
    print(out)

    print(f"文章 URL: {ssh_tunnel.SITE_DOMAIN}/new/article-{article['id']}.html")


if __name__ == '__main__':
    main()
