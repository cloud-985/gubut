#!/usr/bin/env python3
"""上传 /workspace/ai_article.json 到服务器并调用 _publish_ai.js 发布。

_publish_ai.js 会: 追加 articles.json -> 生成含完整 SEO 的文章页 -> 更新 sitemap.xml
                    -> 记录 .published-articles.json -> 修复文件权限。
"""
import base64
import json
import os
import sys
from ssh_tunnel import run_remote

SITE_DIR = "/www/wwwroot/gubut"
LOCAL = "/workspace/ai_article.json"


def main():
    if not os.path.exists(LOCAL):
        print("[ERR] 未找到", LOCAL)
        return 2

    with open(LOCAL, encoding="utf-8") as f:
        content = f.read()

    # 校验本地 JSON 合法
    article = json.loads(content)
    for k in ("id", "title", "date", "content"):
        if not article.get(k):
            print("[ERR] ai_article.json 缺少必填字段:", k)
            return 3
    print("本地 ai_article.json 校验通过: id=%s, title=%s" % (article["id"], article["title"]))

    # 上传到服务器 (base64 避免转义问题)
    b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
    out, err, code = run_remote("echo %s | base64 -d > %s/ai_article.json" % (b64, SITE_DIR), timeout=60)
    if code != 0:
        print("[ERR] 上传失败:", err)
        return code
    print("已上传 ai_article.json 到服务器")

    # 执行发布
    out, err, code = run_remote("cd %s && node _publish_ai.js" % SITE_DIR, timeout=180)
    print(out)
    if err.strip():
        print("[stderr]", err, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
