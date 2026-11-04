#!/usr/bin/env python3
"""上传 ai_article.json 到服务器并调用 _publish_ai.js 发布。"""
import os
import sys

from ssh_tunnel import put_file, run_remote

LOCAL = "/workspace/ai_article.json"
REMOTE = "/www/wwwroot/gubut/ai_article.json"


def main():
    if not os.path.exists(LOCAL):
        sys.stderr.write("[ERR] 未找到 ai_article.json\n")
        return 1
    print("[1/2] 上传 ai_article.json ...")
    put_file(LOCAL, REMOTE)
    print("[2/2] 执行发布脚本 _publish_ai.js ...")
    out, err, code = run_remote("cd /www/wwwroot/gubut && node _publish_ai.js", timeout=180)
    sys.stdout.write(out)
    if err.strip():
        sys.stderr.write(err)
    return code


if __name__ == "__main__":
    sys.exit(main())
