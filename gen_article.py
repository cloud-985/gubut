"""
生成文章JSON文件 - 参考模板
字段：id(毫秒时间戳)、title、date(北京时间)、source、keywords(8-15个)、content
"""
import json
import time
from datetime import datetime, timezone, timedelta


def generate_article_json(title, content_html, source="TradingView精选+AI深度重写", keywords=None):
    """生成标准文章JSON"""
    # 北京时间 (UTC+8)
    beijing_tz = timezone(timedelta(hours=8))
    now_beijing = datetime.now(beijing_tz)
    
    article = {
        "id": int(time.time() * 1000),  # 毫秒时间戳
        "title": title,
        "date": now_beijing.strftime("%Y/%m/%d %H:%M:%S"),
        "source": source,
        "keywords": keywords or [],
        "content": content_html
    }
    
    output_path = "/workspace/ai_article.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 文章JSON已生成: {output_path}")
    print(f"   ID: {article['id']}")
    print(f"   标题: {article['title']}")
    print(f"   日期: {article['date']}")
    print(f"   关键词数量: {len(article['keywords'])}")
    print(f"   内容长度: {len(article['content'])} 字符")
    
    return article, output_path


if __name__ == "__main__":
    # 测试/示例调用
    print("此模块通常由主流程导入使用。")
    print("示例:")
    print("  from gen_article import generate_article_json")
    print("  article, path = generate_article_json('标题', '<p>内容</p>', keywords=['关键词1', '关键词2'])")
