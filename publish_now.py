# -*- coding: utf-8 -*-
"""上传 ai_article.json 到服务器并发布文章。

流程:
  1. 上传本地 /workspace/ai_article.json -> 服务器 /www/wwwroot/gubut/ai_article.json
  2. 在服务器执行 node _publish_ai.js (追加 articles.json、生成文章页、更新 sitemap)
"""
import os
import sys
import ssh_tunnel

LOCAL_JSON = "/workspace/ai_article.json"
REMOTE_JSON = "/www/wwwroot/gubut/ai_article.json"


def main():
    if not os.path.exists(LOCAL_JSON):
        print("本地 ai_article.json 不存在", file=sys.stderr)
        sys.exit(1)

    print("上传 ai_article.json ...")
    ssh_tunnel.put_file(LOCAL_JSON, REMOTE_JSON)
    print("上传完成。执行远程发布...")

    out, err, code = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && node _publish_ai.js", timeout=180
    )
    print(out)
    if err.strip():
        print(err, file=sys.stderr)
    sys.exit(code)


if __name__ == "__main__":
    main()
