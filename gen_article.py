"""
参考脚本：用 Python json.dump 生成合法 ai_article.json
字段：id(毫秒时间戳)、title、date(北京时间)、source、keywords(8-15个)、content
"""
import json
import time
from datetime import datetime, timezone, timedelta


BEIJING_TZ = timezone(timedelta(hours=8))


def beijing_now_str():
    return datetime.now(BEIJING_TZ).strftime("%Y/%m/%d %H:%M:%S")


def build_article(title, content_html, source_url, keywords, article_id=None):
    """构建文章字典"""
    if article_id is None:
        article_id = int(time.time() * 1000)
    if isinstance(keywords, list):
        kw_list = keywords
    else:
        kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
    # 确保8-15个关键词
    if len(kw_list) < 8:
        # 补足通用关键词
        extras = ["量化交易", "技术分析", "MT5", "EA策略", "风险管理", "交易系统", "市场分析", "自动化交易", "区块链", "加密货币", "黄金交易", "外汇交易"]
        for ex in extras:
            if ex not in kw_list:
                kw_list.append(ex)
            if len(kw_list) >= 8:
                break
    kw_list = kw_list[:15]

    return {
        "id": article_id,
        "title": title.strip(),
        "date": beijing_now_str(),
        "source": source_url.strip() if source_url else "TradingView",
        "keywords": kw_list,
        "content": content_html.strip()
    }


def save_article(article, output_path="/workspace/ai_article.json"):
    """保存为JSON并验证"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)
    print(f"文章已写入 {output_path}")
    # 验证
    with open(output_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["id"]
    assert loaded["title"]
    assert loaded["date"]
    assert isinstance(loaded["keywords"], list) and 8 <= len(loaded["keywords"]) <= 15
    assert loaded["content"]
    print(f"验证通过: id={loaded['id']}, 标题={loaded['title'][:50]}, 关键词={len(loaded['keywords'])}个")
    # 字数统计（去除HTML标签）
    import re
    plain = re.sub(r"<[^>]+>", "", loaded["content"])
    plain = re.sub(r"\s+", "", plain)
    print(f"正文字数(去HTML标签): {len(plain)} 字")
    return loaded


if __name__ == "__main__":
    # 示例使用
    sample_title = "示例文章标题"
    sample_content = "<p>这是示例文章内容</p>"
    sample_source = "https://example.com"
    sample_keywords = ["比特币", "BTC", "技术分析", "量化交易", "支撑位", "阻力位", "交易策略", "风险管理"]
    art = build_article(sample_title, sample_content, sample_source, sample_keywords)
    save_article(art)
