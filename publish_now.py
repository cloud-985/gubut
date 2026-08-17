"""上传 /workspace/ai_article.json 并发布到 gubut.com。

流程:
  1. 校验 /workspace/ai_article.json 合法
  2. 通过 SSH 上传 ai_article.json 到 /www/wwwroot/gubut/ai_article.json
  3. 通过 SSH 上传 _publish_ai.js 到 /www/wwwroot/gubut/_publish_ai.js
  4. 远程执行 `node /www/wwwroot/gubut/_publish_ai.js` 完成发布:
     - 追加 articles.json (新文章放顶部, 自动去重)
     - 生成 new/article-{id}.html (含完整 SEO: title/keywords/description/canonical/OG/Twitter/JSON-LD)
     - 更新 sitemap.xml
     - 记录到 .published-articles.json
     - 修复 www:www 权限
  5. 远程校验文章页是否生成、sitemap 是否含新 URL
"""
import json
import os
import sys

from ssh_tunnel import ssh_tunnel, REMOTE_ROOT

LOCAL_AI = "/workspace/ai_article.json"
LOCAL_PUB_JS = "/workspace/_publish_ai.js"
REMOTE_AI = f"{REMOTE_ROOT}/ai_article.json"
REMOTE_PUB_JS = f"{REMOTE_ROOT}/_publish_ai.js"


def main():
    # 1. 校验本地 ai_article.json
    if not os.path.exists(LOCAL_AI):
        print(f"[ERR] {LOCAL_AI} 不存在, 先运行 gen_article.py", file=sys.stderr)
        sys.exit(2)
    try:
        with open(LOCAL_AI, "r", encoding="utf-8") as fp:
            article = json.load(fp)
    except Exception as e:
        print(f"[ERR] {LOCAL_AI} JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(3)
    for k in ["id", "title", "date", "source", "keywords", "content"]:
        if k not in article:
            print(f"[ERR] ai_article.json 缺少字段: {k}", file=sys.stderr)
            sys.exit(4)
    print(f"[OK] 本地 ai_article.json 校验通过: id={article['id']}, title={article['title']}")

    # 2. 上传 ai_article.json
    print(f"[1/4] 上传 ai_article.json → {REMOTE_AI}")
    ssh_tunnel.put_remote(LOCAL_AI, REMOTE_AI)
    # 3. 上传 _publish_ai.js
    print(f"[2/4] 上传 _publish_ai.js → {REMOTE_PUB_JS}")
    ssh_tunnel.put_remote(LOCAL_PUB_JS, REMOTE_PUB_JS)

    # 4. 远程执行发布脚本
    print(f"[3/4] 远程执行: node {REMOTE_PUB_JS}")
    out, err, code = ssh_tunnel.run_remote(
        f"node {REMOTE_PUB_JS} 2>&1", timeout=120
    )
    print(out)
    if err.strip():
        print("STDERR:", err)
    if code != 0:
        print(f"[ERR] 发布脚本退出码非零: {code}", file=sys.stderr)
        sys.exit(5)

    # 5. 校验
    article_id = article["id"]
    article_url = f"https://www.gubut.com/new/article-{article_id}.html"
    remote_html = f"{REMOTE_ROOT}/new/article-{article_id}.html"
    print(f"[4/4] 校验发布结果")
    out, _, _ = ssh_tunnel.run_remote(f"test -f {remote_html} && echo HTML_OK || echo HTML_MISSING")
    print(f"  文章页 {remote_html}: {out.strip()}")
    out, _, _ = ssh_tunnel.run_remote(f"grep -c '{article_url}' {REMOTE_ROOT}/sitemap.xml")
    print(f"  sitemap 含新 URL 次数: {out.strip()}")
    out, _, _ = ssh_tunnel.run_remote(
        f"python3 -c \"import json; arts=json.load(open('{REMOTE_ROOT}/articles.json')); "
        f"print('articles_count=' + str(len(arts))); "
        f"print('top_id=' + str(arts[0].get('id')) if arts else 'empty')\""
    )
    print(f"  articles.json: {out.strip().replace(chr(10), ' | ')}")

    print()
    print("=" * 60)
    print(f"发布完成 ✓")
    print(f"文章标题: {article['title']}")
    print(f"文章 URL : {article_url}")
    import re
    plain = re.sub(r"<[^>]+>", "", article["content"])
    plain_no_space = re.sub(r"\s+", "", plain)
    print(f"正文字数 : {len(plain_no_space)} 字")
    print("=" * 60)


if __name__ == "__main__":
    main()
