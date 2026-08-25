import json
import requests
import sys
import os

PROXY = {'http': 'http://127.0.0.1:18080', 'https': 'http://127.0.0.1:18080'}
API_BASE = 'https://www.gubut.com'
ARTICLE_FILE = '/workspace/ai_article.json'


def load_article():
    with open(ARTICLE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def publish_via_api(article):
    """通过网站API发布文章"""
    url = f'{API_BASE}/api/save-article'
    try:
        resp = requests.post(url, json=article, timeout=30, proxies=PROXY)
        print(f'API响应状态: {resp.status_code}')
        if resp.status_code == 200:
            result = resp.json()
            print(f'API响应: {json.dumps(result, ensure_ascii=False, indent=2)}')
            if result.get('success'):
                return True, result.get('message', '发布成功')
            else:
                return False, result.get('message', '发布失败')
        else:
            return False, f'HTTP {resp.status_code}: {resp.text[:200]}'
    except Exception as e:
        return False, f'API调用异常: {e}'


def publish_via_ssh(article):
    """通过SSH直接操作服务器文件"""
    try:
        sys.path.insert(0, '/workspace')
        from ssh_tunnel import run_remote, REMOTE_BASE
        import base64

        article_b64 = base64.b64encode(
            json.dumps(article, ensure_ascii=False).encode('utf-8')
        ).decode('ascii')

        script = f'''
import json, os, base64

article_data = json.loads(base64.b64decode("{article_b64}").decode("utf-8"))
articles_path = "{REMOTE_BASE}/articles.json"

if os.path.exists(articles_path):
    with open(articles_path, "r", encoding="utf-8") as f:
        articles = json.load(f)
else:
    articles = []

articles.insert(0, article_data)

with open(articles_path, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"文章已添加，共{{len(articles)}}篇")
'''

        result = run_remote(f'python3 -c "{script}"', timeout=60)
        if result['exit_code'] == 0:
            print(f'SSH执行成功: {result["stdout"]}')

            result2 = run_remote(f'cd {REMOTE_BASE} && node build.js', timeout=60)
            if result2['exit_code'] == 0:
                print(f'构建成功: {result2["stdout"]}')
                return True, '通过SSH发布成功'
            else:
                print(f'构建失败: {result2["stderr"]}')
                return True, '文章已添加但构建失败'
        else:
            return False, f'SSH执行失败: {result["stderr"]}'
    except Exception as e:
        return False, f'SSH方式异常: {e}'


def publish_via_direct_build(article):
    """本地构建HTML并生成文件，然后通过API上传"""
    try:
        sys.path.insert(0, '/workspace')
        from build import generateArticlePage, updateSitemap

        articles_path = '/workspace/articles.json'
        if os.path.exists(articles_path):
            with open(articles_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
        else:
            articles = []

        articles.insert(0, article)

        with open(articles_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

        generateArticlePage(article)
        updateSitemap(articles)

        return True, '本地构建成功'
    except Exception as e:
        return False, f'本地构建异常: {e}'


def main():
    print('=== 开始发布文章 ===')
    article = load_article()
    print(f'文章ID: {article["id"]}')
    print(f'标题: {article["title"]}')
    print()

    methods = [
        ('API接口', publish_via_api),
        ('SSH直连', publish_via_ssh),
        ('本地构建', publish_via_direct_build),
    ]

    for name, method in methods:
        print(f'尝试 [{name}]...')
        success, msg = method(article)
        if success:
            print(f'  ✓ 成功: {msg}')
            print(f'\n=== 发布完成 ===')
            print(f'文章URL: https://www.gubut.com/new/article-{article["id"]}.html')
            return True
        else:
            print(f'  ✗ 失败: {msg}')

    print(f'\n=== 所有发布方式均失败 ===')
    print('文章已保存在 /workspace/ai_article.json，可手动上传')
    return False


if __name__ == '__main__':
    main()
