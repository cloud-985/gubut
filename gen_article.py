#!/usr/bin/env python3
"""生成 ai_article.json 文件的参考脚本"""

import json
import time
from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))


def generate_article_json(title, content, source="TradingView精选", keywords=None):
    """
    生成标准格式的文章JSON
    
    参数:
        title: 文章标题 (中文)
        content: HTML格式的文章正文
        source: 文章来源描述
        keywords: 关键词列表 (8-15个)
    
    返回:
        dict: 标准格式的文章对象
    """
    if keywords is None:
        keywords = [
            "BTC", "交易策略", "技术分析", "MT5", "EA交易",
            "支撑位", "阻力位", "风险管理", "黄金XAUUSD", "外汇"
        ]
    
    # 确保关键词数量在8-15个之间
    if len(keywords) < 8:
        base_kw = ["技术分析", "交易策略", "风险管理", "MT5", "EA自动化"]
        for kw in base_kw:
            if kw not in keywords:
                keywords.append(kw)
            if len(keywords) >= 8:
                break
    
    article = {
        "id": int(time.time() * 1000),  # 毫秒时间戳
        "title": title,
        "date": datetime.now(BEIJING_TZ).strftime('%Y/%m/%d %H:%M:%S'),  # 北京时间
        "source": source,
        "keywords": keywords[:15],  # 最多15个
        "content": content
    }
    
    return article


def save_article_json(article, filepath="/workspace/ai_article.json"):
    """保存文章到JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(article, f, ensure_ascii=False, indent=2)
    print(f"文章已保存到 {filepath}")
    print(f"  ID: {article['id']}")
    print(f"  标题: {article['title']}")
    print(f"  日期: {article['date']}")
    print(f"  关键词: {', '.join(article['keywords'])}")
    print(f"  内容长度: {len(article['content'])} 字符")
    return True


def validate_article_json(filepath="/workspace/ai_article.json"):
    """验证JSON文件格式"""
    print(f"\n验证文章JSON: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            article = json.load(f)
        
        # 检查必填字段
        required = ["id", "title", "date", "source", "keywords", "content"]
        for field in required:
            if field not in article:
                print(f"  ❌ 缺少字段: {field}")
                return False
        
        # 检查字段类型
        if not isinstance(article["id"], int):
            print(f"  ❌ id 必须是整数")
            return False
        if not isinstance(article["keywords"], list):
            print(f"  ❌ keywords 必须是列表")
            return False
        if len(article["keywords"]) < 8:
            print(f"  ⚠️  keywords 数量不足8个 (当前{len(article['keywords'])})")
        
        print(f"  ✅ JSON格式验证通过")
        print(f"  ✅ 关键词数量: {len(article['keywords'])}个")
        print(f"  ✅ 正文字符数: {len(article['content'])}字")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON解析失败: {e}")
        return False
    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
        return False


if __name__ == "__main__":
    # 示例：创建一篇测试文章
    test_title = "测试文章：BTC技术分析与交易策略"
    test_content = """<h2>一、行情概述</h2>
<p>近期BTC市场波动剧烈...</p>
<h2>二、关键价位</h2>
<p>支撑位：60000 阻力位：70000</p>
<h2>三、技术分析</h2>
<p>MACD出现金叉信号...</p>
<h2>四、交易策略</h2>
<p>策略一：突破买入法...</p>
<h2>五、风险管理</h2>
<p>设置止损止盈...</p>
<h2>六、MT5/EA自动化执行</h2>
<p>通过MT5 EA自动执行...</p>
<h2>七、总结</h2>
<p>综合来看...</p>"""
    
    test_keywords = ["BTC", "比特币", "技术分析", "交易策略", "MT5", "EA交易", 
                     "支撑位", "阻力位", "风险管理", "加密货币"]
    
    article = generate_article_json(test_title, test_content, keywords=test_keywords)
    save_article_json(article)
    validate_article_json()
