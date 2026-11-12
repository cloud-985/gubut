#!/usr/bin/env python3
"""发布 ai_article.json 到服务器并执行 node publish_ai.js。"""
import json
import sys
import ssh_tunnel

LOCAL_FILE = "/workspace/ai_article.json"
REMOTE_FILE = "/www/wwwroot/gubut/ai_article.json"
SITE_DIR = "/www/wwwroot/gubut"
SITE_DOMAIN = "https://www.gubut.com"


def main():
    # 读取并校验本地文件
    try:
        article = json.load(open(LOCAL_FILE, "r", encoding="utf-8"))
    except Exception as e:
        print("[错误] 无法读取 ai_article.json:", e)
        raise SystemExit(1)

    required = ["id", "title", "content"]
    missing = [k for k in required if not article.get(k)]
    if missing:
        print("[错误] ai_article.json 缺少字段:", missing)
        raise SystemExit(1)

    print(f"文章标题: {article.get('title')}")
    print(f"文章ID: {article.get('id')}")
    print(f"正文字符数: {len(article.get('content', ''))}")

    # 上传
    data = json.dumps(article, ensure_ascii=False, indent=2).encode("utf-8")
    ssh_tunnel.put_file_bytes(REMOTE_FILE, data)
    print(f"已上传 ai_article.json 到服务器")

    # 发布
    cmd = f"cd {SITE_DIR} && node publish_ai.js"
    out, err, code = ssh_tunnel.run_remote(cmd, timeout=180)
    print(out, end="")
    if err:
        print("STDERR:", err)
    if code != 0:
        print("[发布失败] exit code", code)
        raise SystemExit(code)

    url = f"{SITE_DOMAIN}/new/article-{article['id']}.html"
    print(f"\n发布成功 URL: {url}")
    return url


if __name__ == "__main__":
    main()
