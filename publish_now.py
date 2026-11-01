# -*- coding: utf-8 -*-
"""上传 ai_article.json 到服务器并发布。

流程(复用服务器端 _publish_ai.js):
  1. 上传 /workspace/ai_article.json -> /www/wwwroot/gubut/ai_article.json
  2. 在服务器端执行 `node _publish_ai.js`
      - 追加到 articles.json
      - 生成 new/article-{id}.html (含完整 SEO 标签)
      - 更新 sitemap.xml
      - 追加 .published-articles.json
"""
import os

import ssh_tunnel

LOCAL_AI = "/workspace/ai_article.json"
REMOTE_AI = "/www/wwwroot/gubut/ai_article.json"


def main():
    if not os.path.exists(LOCAL_AI):
        raise SystemExit("未找到 ai_article.json, 请先运行 gen_article.py")

    print("[publish] 上传 ai_article.json 到服务器 ...")
    ssh_tunnel.upload(LOCAL_AI, REMOTE_AI)
    print("[publish] 上传完成:", REMOTE_AI)

    print("[publish] 在服务器端执行发布脚本 _publish_ai.js ...")
    out, err = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && /usr/bin/node _publish_ai.js 2>&1", timeout=300
    )
    print(out)
    if err.strip():
        print("[publish] STDERR:", err.strip())


if __name__ == "__main__":
    main()
