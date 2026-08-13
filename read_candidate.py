#!/usr/bin/env python3
"""读取远程服务器 pending-articles.json 的前N篇候选文章"""

import json
import sys
import os
from ssh_tunnel import run_remote, REMOTE_DIR

REMOTE_CANDIDATE_FILE = f"{REMOTE_DIR}/pending-articles.json"
LOCAL_CANDIDATE_FILE = "/workspace/pending-articles.json"


def read_candidates_from_remote(count=8):
    """从远程服务器读取候选文章"""
    print(f"从远程服务器读取候选文章 (最多{count}篇)...")
    
    # 读取远程JSON文件内容
    content = run_remote(f"cat {REMOTE_CANDIDATE_FILE}")
    
    if not content or not content.strip():
        print("远程候选文件为空或不存在!")
        return []
    
    try:
        articles = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"内容预览: {content[:500]}")
        return []
    
    print(f"远程服务器共有 {len(articles)} 篇候选文章")
    
    # 取前N篇
    selected = articles[:count]
    print(f"选取前 {len(selected)} 篇候选文章")
    
    # 输出摘要信息
    for i, art in enumerate(selected):
        print(f"\n  [{i+1}] 标题: {art.get('title', '无标题')[:60]}")
        print(f"      来源: {art.get('source', '未知')}")
        print(f"      发布: {art.get('published', '')[:30]}")
        print(f"      标签: {', '.join(art.get('tags', [])[:5])}")
        content_len = len(art.get('content', '') or art.get('summary', ''))
        print(f"      内容长度: {content_len} 字符")
    
    # 保存到本地供后续处理
    with open(LOCAL_CANDIDATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)
    print(f"\n已保存到本地: {LOCAL_CANDIDATE_FILE}")
    
    return selected


def read_published_articles():
    """读取已发布文章用于主题去重判断"""
    print("\n读取已发布文章列表...")
    
    # 先尝试从远程读取
    content = run_remote(f"cat {REMOTE_DIR}/articles.json")
    
    if not content:
        print("远程 articles.json 为空，尝试本地articles.json...")
        if os.path.exists("/workspace/articles.json"):
            with open("/workspace/articles.json", 'r', encoding='utf-8') as f:
                articles = json.load(f)
        else:
            return []
    else:
        try:
            articles = json.loads(content)
        except:
            return []
    
    print(f"已发布文章 {len(articles)} 篇")
    
    # 只保留最近的标题用于比对
    recent = []
    for art in articles[:20]:  # 最近20篇
        recent.append({
            'title': art.get('title', ''),
            'date': art.get('date', '')
        })
    
    return recent


if __name__ == "__main__":
    count = 8
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    
    candidates = read_candidates_from_remote(count)
    published = read_published_articles()
    
    # 输出已发布文章标题供参考
    print("\n最近已发布文章:")
    for i, art in enumerate(published[:10]):
        print(f"  [{i+1}] {art['title'][:50]} ({art['date'][:10]})")
