import json
import sys
import time
import datetime

OUT = "/workspace/ai_article.json"


def beijing_now_str():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    return now.strftime("%Y年%m月%d日 %H:%M")


def main():
    args = {}
    for a in sys.argv[1:]:
        if a.startswith("--"):
            k, _, v = a[2:].partition("=")
            args[k] = v

    title = args.get("title", "")
    date = args.get("date") or beijing_now_str()
    source = args.get("source", "")
    keywords = [k.strip() for k in args.get("keywords", "").split(",") if k.strip()]
    content_file = args.get("content-file", "")
    if not content_file:
        print("缺少 --content-file 参数")
        sys.exit(1)

    with open(content_file, encoding="utf-8") as f:
        content = f.read()

    article = {
        "id": int(time.time() * 1000),
        "title": title,
        "date": date,
        "source": source,
        "keywords": keywords,
        "content": content,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)

    print(f"已生成 {OUT}")
    print(f"  id={article['id']}")
    print(f"  title={article['title']}")
    print(f"  keywords 数量={len(keywords)}")
    print(f"  content 字符数={len(content)}")


if __name__ == "__main__":
    main()
