#!/usr/bin/env python3
"""上传 ai_article.json 到服务器并执行发布,然后验证。"""
import os
import sys
import json
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ssh_tunnel

SITE_DIR = "/www/wwwroot/gubut"
SITE_DOMAIN = "https://www.gubut.com"
LOCAL_FILE = "/workspace/ai_article.json"


def main():
    if not os.path.exists(LOCAL_FILE):
        print("[ERR] ai_article.json 不存在")
        sys.exit(1)

    article = json.load(open(LOCAL_FILE, encoding="utf-8"))
    article_id = article["id"]
    title = article["title"]
    url = SITE_DOMAIN + "/new/article-" + str(article_id) + ".html"

    print("[1/3] 上传 ai_article.json 到服务器 ...")
    ssh_tunnel.put_file(LOCAL_FILE, SITE_DIR + "/ai_article.json")
    print("[OK] 已上传")

    print("[2/3] 执行服务器发布脚本 _publish_ai.js ...")
    out, err, code = ssh_tunnel.run_remote(
        "cd {d} && node _publish_ai.js 2>&1".format(d=SITE_DIR),
        timeout=180,
    )
    print(out)
    if err.strip():
        print("[stderr]", err)
    print("[发布脚本退出码]", code)

    print("[3/3] 验证发布结果 ...")
    # 1) articles.json 是否包含新 id
    check_articles = (
        "python3 -c \"import json; d=json.load(open('{d}/articles.json')); "
        "print([a for a in d if str(a.get('id'))==str({i})])\"".format(d=SITE_DIR, i=article_id)
    )
    out, err, code = ssh_tunnel.run_remote(check_articles, timeout=60)
    print("articles.json 命中:", out.strip()[:200])

    # 2) 文章页是否存在 + SEO 标签检查
    out, err, code = ssh_tunnel.run_remote(
        "ls -la {d}/new/article-{i}.html && "
        "grep -oE '<title>[^<]*</title>|name=\"keywords\" content=\"[^\"]*\"|name=\"description\" content=\"[^\"]*\"|rel=\"canonical\" href=\"[^\"]*\"|property=\"og:title\" content=\"[^\"]*\"' "
        "{d}/new/article-{i}.html".format(d=SITE_DIR, i=article_id),
        timeout=60,
    )
    print("文章页SEO检查:")
    print(out)

    # 3) sitemap 是否包含新 URL
    out, err, code = ssh_tunnel.run_remote(
        "grep -c 'article-{i}.html' {d}/sitemap.xml".format(d=SITE_DIR, i=article_id),
        timeout=60,
    )
    print("sitemap 命中次数:", out.strip())

    print()
    print("=" * 60)
    print("发布完成")
    print("标题:", title)
    print("URL:", url)
    print("字数:", len(re.sub(r"<[^>]+>", "", article["content"]).replace("\n", "").replace(" ", "")))
    print("=" * 60)


if __name__ == "__main__":
    main()
