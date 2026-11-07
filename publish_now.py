#!/usr/bin/env python3
"""上传 ai_article.json 到服务器并执行发布脚本。"""
import json
import ssh_tunnel

REMOTE_AI = '/www/wwwroot/gubut/ai_article.json'
SITE_DIR = '/www/wwwroot/gubut'


def main():
    # 1. 本地校验
    with open('/workspace/ai_article.json', encoding='utf-8') as f:
        article = json.load(f)
    print('本地文章 id:', article['id'])
    print('标题:', article['title'])

    # 2. 上传
    ssh_tunnel.put_file('/workspace/ai_article.json', REMOTE_AI)
    print('已上传 ai_article.json 到服务器')

    # 3. 执行发布
    r = ssh_tunnel.run_remote(f'cd {SITE_DIR} && node _publish_ai.js', timeout=120)
    print('--- 发布输出 ---')
    print(r['stdout'])
    if r['stderr']:
        print('--- stderr ---')
        print(r['stderr'])
    print('exit_code:', r['exit_code'])

    url = f'https://www.gubut.com/new/article-{article["id"]}.html'
    print('文章 URL:', url)


if __name__ == '__main__':
    main()
