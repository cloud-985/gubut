"""
生成 ai_article.json 文件

用法: python3 gen_article.py --title "标题" --date "2025/08/16 14:30:00" 
                             --source "TradingView" --keywords "kw1,kw2,..." --content-file content.html
或直接通过代码调用 generate_ai_article()
"""
import json
import time
import sys
import os
import argparse
from datetime import datetime, timezone, timedelta


BEIJING_TZ = timezone(timedelta(hours=8))


def beijing_now_str() -> str:
    """返回当前北京时间格式化字符串"""
    return datetime.now(tz=BEIJING_TZ).strftime("%Y/%m/%d %H:%M:%S")


def ms_timestamp_id() -> int:
    """毫秒级时间戳作为文章ID"""
    return int(time.time() * 1000)


def generate_ai_article(title: str, content_html: str, source: str = "TradingView",
                        keywords: list = None, article_id: int = None,
                        date_str: str = None) -> dict:
    """
    生成文章字典对象
    
    Args:
        title: 文章标题
        content_html: HTML格式正文
        source: 文章来源
        keywords: 关键词列表(8-15个)
        article_id: 文章ID（毫秒时间戳），不传则自动生成
        date_str: 发布日期字符串，不传则使用当前北京时间
    
    Returns:
        标准文章字典
    """
    if keywords is None:
        keywords = []

    article = {
        "id": article_id or ms_timestamp_id(),
        "title": title.strip(),
        "date": date_str or beijing_now_str(),
        "source": source,
        "keywords": keywords[:15],  # 最多15个
        "content": content_html,
    }
    return article


def save_ai_article_json(article: dict, output_path: str = "/workspace/ai_article.json") -> str:
    """保存文章为JSON文件（使用json.dump确保合法）"""
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)
    print(f"[生成] 文章JSON已保存: {output_path}")
    return output_path


def validate_ai_article_json(path: str = "/workspace/ai_article.json") -> bool:
    """用Python json.load验证JSON文件合法性并检查必填字段"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_fields = ["id", "title", "date", "source", "keywords", "content"]
        missing = [k for k in required_fields if k not in data]
        if missing:
            print(f"[验证] ❌ 缺少字段: {missing}")
            return False

        if not isinstance(data["id"], int) or data["id"] < 1_000_000_000_000:
            print(f"[验证] ❌ id字段不合法 (应为毫秒时间戳整数): {data['id']}")
            return False

        if len(data["title"]) < 5:
            print(f"[验证] ❌ 标题过短")
            return False

        kw_count = len(data["keywords"])
        if kw_count < 8 or kw_count > 15:
            print(f"[验证] ⚠️  关键词数量应为8-15个，当前: {kw_count}")
            # 不严格失败，但给出警告

        # 统计正文字数（移除HTML标签后）
        import re
        plain_text = re.sub(r"<[^>]+>", "", data["content"])
        plain_text = re.sub(r"\s+", "", plain_text)
        char_count = len(plain_text)
        print(f"[验证] 正文字数(去HTML): {char_count} 字")

        if char_count < 2000:
            print(f"[验证] ⚠️  正文偏少，建议2500-4000字")
        elif char_count > 4500:
            print(f"[验证] ⚠️  正文偏长，建议2500-4000字")

        print(f"[验证] ✅ JSON格式合法，字段完整")
        print(f"       - ID: {data['id']}")
        print(f"       - 标题: {data['title']}")
        print(f"       - 日期: {data['date']}")
        print(f"       - 来源: {data['source']}")
        print(f"       - 关键词({kw_count}): {', '.join(data['keywords'])}")
        return True
    except json.JSONDecodeError as e:
        print(f"[验证] ❌ JSON解析失败: {e}")
        return False
    except FileNotFoundError:
        print(f"[验证] ❌ 文件不存在: {path}")
        return False
    except Exception as e:
        print(f"[验证] ❌ 未知错误: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="生成 ai_article.json")
    parser.add_argument("--title", required=False, help="文章标题")
    parser.add_argument("--content-file", required=False, help="HTML内容文件路径")
    parser.add_argument("--source", default="TradingView", help="来源")
    parser.add_argument("--keywords", default="", help="逗号分隔的关键词")
    parser.add_argument("--output", default="/workspace/ai_article.json", help="输出路径")
    args = parser.parse_args()

    # 交互模式：如果不传参数，提示用法
    if not args.title and not args.content_file:
        print("用法示例:")
        print("  python3 gen_article.py --title '标题' --content-file ./content.html --keywords 'kw1,kw2'")
        print()
        print("或在Python代码中使用:")
        print("  from gen_article import generate_ai_article, save_ai_article_json, validate_ai_article_json")
        print("  article = generate_ai_article(title, content_html, keywords=[...])")
        print("  save_ai_article_json(article)")
        print("  validate_ai_article_json()")
        sys.exit(0)

    if not args.title or not args.content_file:
        print("错误: --title 和 --content-file 必须同时提供")
        sys.exit(1)

    # 读取内容文件
    if not os.path.exists(args.content_file):
        print(f"错误: 内容文件不存在: {args.content_file}")
        sys.exit(1)
    with open(args.content_file, "r", encoding="utf-8") as f:
        content_html = f.read()

    # 解析关键词
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else []

    article = generate_ai_article(
        title=args.title,
        content_html=content_html,
        source=args.source,
        keywords=keywords,
    )
    save_ai_article_json(article, args.output)
    ok = validate_ai_article_json(args.output)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
