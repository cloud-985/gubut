import ssh_tunnel

LOCAL_FILE = "/workspace/ai_article.json"
REMOTE_FILE = "/www/wwwroot/gubut/ai_article.json"

if __name__ == "__main__":
    print("[上传] 上传 ai_article.json 到服务器...")
    ssh_tunnel.put_file(LOCAL_FILE, REMOTE_FILE)
    print("[上传] 完成")

    print("[发布] 执行 node _publish_ai.js ...")
    code, out, err = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && node _publish_ai.js"
    )
    print(out)
    if err.strip():
        print("STDERR:", err)
    raise SystemExit(code)
