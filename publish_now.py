#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""上传 ai_article.json 到服务器并执行 node publish_ai.js 发布。"""
import ssh_tunnel as st

LOCAL_JSON = "/workspace/ai_article.json"
REMOTE_JSON = "/www/wwwroot/gubut/ai_article.json"


def main():
    print("上传 ai_article.json ->", REMOTE_JSON)
    st.put_file(LOCAL_JSON, REMOTE_JSON)
    print("上传完成，开始发布...\n")

    code, out, err = st.run_remote(
        "cd /www/wwwroot/gubut && node publish_ai.js 2>&1", timeout=180
    )
    print(out)
    if err and err.strip():
        print("STDERR:", err)
    print("exit code:", code)


if __name__ == "__main__":
    main()
