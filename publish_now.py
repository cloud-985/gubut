import json

import ssh_tunnel as s

LOCAL_AI_FILE = "/workspace/ai_article.json"
REMOTE_AI_FILE = "/www/wwwroot/gubut/ai_article.json"
REMOTE_PUBLISH = "cd /www/wwwroot/gubut && node publish_ai.js"


def main():
    with open(LOCAL_AI_FILE, "r", encoding="utf-8") as f:
        article = json.load(f)

    s.put_file(LOCAL_AI_FILE, REMOTE_AI_FILE)
    print("已上传 ai_article.json 到服务器")

    out, err, code = s.run_remote(REMOTE_PUBLISH, timeout=180)
    print(out)
    if err.strip():
        print("STDERR:", err)
    print("exit:", code)

    if code != 0:
        print("发布失败，退出码", code)
        return code

    url = "https://www.gubut.com/new/article-%s.html" % article["id"]
    print("发布完成")
    print("文章标题:", article["title"])
    print("文章URL:", url)
    print("字数(内容字符数):", len(article["content"]))
    return code


if __name__ == "__main__":
    main()
