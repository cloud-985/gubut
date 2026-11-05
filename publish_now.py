"""上传本地 ai_article.json 到服务器并执行发布 (_publish_ai.js)。"""
import os
import sys
import ssh_tunnel

LOCAL = "/workspace/ai_article.json"
REMOTE = "/www/wwwroot/gubut/ai_article.json"

if __name__ == "__main__":
    if not os.path.exists(LOCAL):
        print(f"本地 {LOCAL} 不存在")
        sys.exit(2)
    print("上传 ai_article.json ...")
    ssh_tunnel.put_file(LOCAL, REMOTE)
    print("上传完成, 开始发布 ...")
    out, err, code = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && node _publish_ai.js", timeout=90
    )
    print(out, end="")
    if err:
        print("STDERR:", err)
    raise SystemExit(code)
