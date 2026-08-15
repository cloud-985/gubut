#!/usr/bin/env python3
"""publish_now.py - 上传本地 ai_article.json 到服务器并发布

流程:
1. 上传 /workspace/ai_article.json -> /www/wwwroot/gubut/ai_article.json
2. 上传 /workspace/publish_ai.js 与 update_ai.js
3. 通过 SSH 执行: cd /www/wwwroot/gubut && node publish_ai.js
   若该 id 已存在(publish_ai.js 退出码 2), 自动改用 update_ai.js 更新
4. 抓取文章页 HTML 验证 SEO 标签 / sitemap 含新 URL
"""
import sys
import os
import re
from ssh_tunnel import ssh_tunnel

LOCAL_AI = "/workspace/ai_article.json"
LOCAL_JS_PUBLISH = "/workspace/publish_ai.js"
LOCAL_JS_UPDATE = "/workspace/update_ai.js"
REMOTE_AI = "/www/wwwroot/gubut/ai_article.json"
REMOTE_JS_PUBLISH = "/www/wwwroot/gubut/publish_ai.js"
REMOTE_JS_UPDATE = "/www/wwwroot/gubut/update_ai.js"


def main():
    if not os.path.exists(LOCAL_AI):
        print(f"[发布] 缺少 {LOCAL_AI}, 请先运行 gen_article.py", file=sys.stderr)
        sys.exit(1)

    print("[发布] 上传 ai_article.json 与发布脚本到服务器 ...")
    ssh_tunnel.put_file(LOCAL_AI, REMOTE_AI)
    ssh_tunnel.put_file(LOCAL_JS_PUBLISH, REMOTE_JS_PUBLISH)
    if os.path.exists(LOCAL_JS_UPDATE):
        ssh_tunnel.put_file(LOCAL_JS_UPDATE, REMOTE_JS_UPDATE)
    print("[发布] 上传完成")

    # 先尝试新发布
    print("[发布] 执行 node publish_ai.js ...")
    rc, out, err = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && node publish_ai.js 2>&1", timeout=120
    )
    print(out)
    if err:
        print("[STDERR]", err, file=sys.stderr)

    # 退出码 2 = id 已存在, 改用 update_ai.js
    if rc == 2:
        print("[发布] 文章 id 已存在, 改用 update_ai.js 更新 ...")
        rc, out, err = ssh_tunnel.run_remote(
            "cd /www/wwwroot/gubut && node update_ai.js 2>&1", timeout=120
        )
        print(out)
        if err:
            print("[STDERR]", err, file=sys.stderr)
    if rc != 0:
        print(f"[发布] 发布失败 rc={rc}", file=sys.stderr)
        sys.exit(rc)

    # 解析文章 URL 用于后续验证
    m = re.search(r"文章URL:\s*(https://\S+)", out)
    article_url = m.group(1) if m else None
    article_id_m = re.search(r"文章ID:\s*(\d+)", out)
    article_id = article_id_m.group(1) if article_id_m else None

    if article_url and article_id:
        print(f"\n[发布] 文章已发布/更新")
        print(f"  URL: {article_url}")
        print(f"  ID : {article_id}")

    ssh_tunnel.close()
    return article_url, article_id


if __name__ == "__main__":
    main()
