#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 ai_article.json 的辅助脚本
用法:
    import gen_article
    gen_article.save_article(article_dict)
    gen_article.validate('/workspace/ai_article.json')
"""

import json
import time
import re
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))


def beijing_now_str():
    return datetime.now(BEIJING_TZ).strftime('%Y/%m/%d %H:%M:%S')


def make_article_id():
    return int(time.time() * 1000)


def strip_html_text(html):
    return re.sub(r'<[^>]+>', '', html)


def count_chinese_chars(html):
    text = strip_html_text(html)
    # 只算中文字符+数字+标点实际长度，空格压缩
    compact = re.sub(r'\s+', '', text)
    return len(compact)


def save_article(title, content_html, source, keywords, output_path='/workspace/ai_article.json'):
    article = {
        'id': make_article_id(),
        'title': title,
        'date': beijing_now_str(),
        'source': source,
        'keywords': keywords,
        'content': content_html,
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(article, f, ensure_ascii=False, indent=2)
    print(f'[OK] 已保存: {output_path}')
    print(f'  id       : {article["id"]}')
    print(f'  title    : {article["title"]}')
    print(f'  date     : {article["date"]}')
    print(f'  source   : {article["source"]}')
    print(f'  keywords : {len(keywords)}个: {",".join(keywords)}')
    print(f'  内容字数(去除HTML) : {count_chinese_chars(content_html)} 字')
    return article


def validate(path='/workspace/ai_article.json'):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f'[FAIL] JSON 解析失败: {e}')
        return False

    required = ['id', 'title', 'date', 'source', 'keywords', 'content']
    missing = [k for k in required if k not in data]
    if missing:
        print(f'[FAIL] 缺少字段: {missing}')
        return False

    errors = []
    if not isinstance(data['id'], int):
        errors.append('id 不是 int(毫秒时间戳)')
    if not isinstance(data['title'], str) or len(data['title']) < 6:
        errors.append('title 过短')
    if not isinstance(data['date'], str) or '/' not in data['date']:
        errors.append('date 格式异常(期望 年/月/日 时:分:秒)')
    if not isinstance(data['source'], str) or len(data['source']) < 2:
        errors.append('source 过短')
    if not isinstance(data['keywords'], list) or not (8 <= len(data['keywords']) <= 15):
        errors.append(f'keywords 应为 8-15 个，实际 {len(data.get("keywords",[]))}')
    if not isinstance(data['content'], str):
        errors.append('content 不是字符串')

    n_chars = count_chinese_chars(data['content'])
    if n_chars < 2400:
        errors.append(f'正文字数不足(至少2500，实际{n_chars})')
    elif n_chars > 4200:
        errors.append(f'正文字数超标(最多4000，实际{n_chars})')

    # 英文残留检查 (除 BTC XAUUSD 等交易代码外，不应有长段英文)
    content_text = strip_html_text(data['content'])
    title_text = data['title']
    all_text = title_text + ' ' + content_text
    # 找连续3个以上英文字母的单词
    english_words = re.findall(r'[A-Za-z]{3,}', all_text)
    allowed = {
        'BTC', 'USDT', 'XAUUSD', 'EURUSD', 'GBPUSD', 'AUDCHF',
        'MT5', 'EA', 'RSI', 'MACD', 'EMA', 'SMA', 'ATR', 'K线',
        'API', 'CTP', 'MEXC', 'REST', 'WebSocket', 'HTML', 'JSON',
        'ETF', 'GDP', 'CPI', 'USD', 'ETH', 'SOL', 'BNB', 'OKX',
        'ETF', 'FOMC', 'TPP', 'RR', 'SL', 'TP', 'R',
    }
    residue = []
    for w in english_words:
        if w.upper() in {a.upper() for a in allowed}:
            continue
        residue.append(w)
    # 允许最多5个意外英文词（个别缩写）
    if len(residue) > 5:
        errors.append(f'英文残留过多: {list(set(residue))[:10]}')

    if errors:
        print(f'[FAIL] 验证未通过:')
        for e in errors:
            print(f'  - {e}')
        return False

    print(f'[PASS] 验证全部通过 ✓')
    print(f'  字数: {n_chars}')
    print(f'  关键词: {len(data["keywords"])}个')
    if residue:
        print(f'  英文词过滤后剩余: {list(set(residue))}')
    return True


if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else '/workspace/ai_article.json'
    validate(path)
