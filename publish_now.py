#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""上传 ai_article.json 并在服务器上运行 publish_ai.js 发布。"""
import os
import ssh_tunnel

LOCAL_FILE = "/workspace/ai_article.json"
REMOTE_FILE = "/www/wwwroot/gubut/ai_article.json"


def main():
    if not os.path.exists(LOCAL_FILE):
        print("[发布] 未找到 %s" % LOCAL_FILE)
        return 1

    print("[发布] 上传 %s -> %s" % (LOCAL_FILE, REMOTE_FILE))
    ssh_tunnel.sftp_put(LOCAL_FILE, REMOTE_FILE)
    print("[发布] 上传完成, 远程执行 publish_ai.js ...")

    code, out, err = ssh_tunnel.run_remote("cd /www/wwwroot/gubut && node publish_ai.js")
    print("exit=%s" % code)
    if out:
        print(out)
    if err:
        print("[stderr]\n%s" % err)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
