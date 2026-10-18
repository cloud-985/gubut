# -*- coding: utf-8 -*-
import ssh_tunnel

LOCAL_FILE = "/workspace/ai_article.json"
REMOTE_FILE = "/www/wwwroot/gubut/ai_article.json"

print("[上传] ai_article.json -> 服务器")
ssh_tunnel.upload_file(LOCAL_FILE, REMOTE_FILE)
print("[上传] 完成")

print("[发布] 执行 node publish_ai.js")
result = ssh_tunnel.run_remote("cd /www/wwwroot/gubut && node publish_ai.js", timeout=180)
print(result["stdout"])
if result["stderr"]:
    print(result["stderr"])
print("[发布] 退出码:", result["code"])
