#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""上传 /workspace/ai_article.json 到 gubut 服务器并触发 _publish_ai.js 发布。"""
import base64
import json
import sys

from ssh_tunnel import run_remote

LOCAL = "/workspace/ai_article.json"
REMOTE = "/www/wwwroot/gubut/ai_article.json"


def main():
    # 1. 本地读取并校验 JSON
    with open(LOCAL, "r", encoding="utf-8") as f:
        article = json.load(f)

    for k in ["id", "title", "date", "content"]:
        if article.get(k) in (None, ""):
            print("ERROR: 缺少必填字段", k)
            sys.exit(1)

    art_id = article["id"]
    print("本地文章: id=%s title=%s" % (art_id, article["title"]))

    # 2. base64 上传（避免引号/换行等转义问题）
    with open(LOCAL, "rb") as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode("ascii")

    # base64 只含 [A-Za-z0-9+/=]，无空格无引号，直接不加引号即可安全传递
    upload_cmd = (
        'echo %s | base64 -d > %s '
        '&& echo UPLOAD_OK '
        '&& ls -l %s' % (b64, REMOTE, REMOTE)
    )
    print("\n--- 上传 ai_article.json ---")
    print(run_remote(upload_cmd, timeout=180))

    # 3. 触发服务器发布脚本
    print("\n--- 执行 node _publish_ai.js ---")
    out = run_remote(
        "cd /www/wwwroot/gubut && node _publish_ai.js", timeout=180
    )
    print(out)

    # 4. 输出文章 URL
    print("\n文章URL: https://www.gubut.com/new/article-%s.html" % art_id)


if __name__ == "__main__":
    main()
