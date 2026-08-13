#!/usr/bin/env python3
"""发布文章到 gubut.com - 上传ai_article.json, 追加到articles.json, 生成文章页, 更新sitemap"""

import json
import os
import sys
import re
import time
from datetime import datetime, timezone, timedelta
from ssh_tunnel import run_remote, upload_file, download_file, REMOTE_DIR

AI_ARTICLE_PATH = "/workspace/ai_article.json"
REMOTE_AI_ARTICLE = f"{REMOTE_DIR}/ai_article.json"
REMOTE_ARTICLES_JSON = f"{REMOTE_DIR}/articles.json"
REMOTE_SITEMAP = f"{REMOTE_DIR}/sitemap.xml"

BEIJING_TZ = timezone(timedelta(hours=8))


def sanitize_url(title):
    """将标题转换为URL友好的slug"""
    # 移除特殊字符，保留中文、字母、数字
    slug = re.sub(r'[^\w\u4e00-\u9fff]', '-', title)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug[:50]  # 限制长度


def generate_article_html(article):
    """生成独立的文章HTML页面"""
    article_id = article['id']
    title = article['title']
    date = article['date']
    content = article['content']
    keywords = ', '.join(article.get('keywords', []))
    source = article.get('source', '')
    
    # 生成简短描述用于SEO (取前200字纯文本)
    desc_text = re.sub(r'<[^>]+>', '', content)
    desc_text = re.sub(r'\s+', ' ', desc_text).strip()
    description = desc_text[:200] + '...' if len(desc_text) > 200 else desc_text
    
    url_slug = sanitize_url(title)
    canonical_url = f"https://www.gubut.com/article-{article_id}.html"
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 谷比算力</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <meta name="author" content="谷比算力">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="谷比算力">
    <meta property="article:published_time" content="{date.replace('/', '-')}">
    <meta property="article:tag" content="{keywords}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{canonical_url}">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    
    <!-- Canonical -->
    <link rel="canonical" href="{canonical_url}">
    
    <link rel="stylesheet" href="styles.css">
    <link rel="icon" href="favicon.ico">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <a href="index.html" class="logo">
                <img src="img/logo.png" alt="谷比算力">
                <span>谷比算力</span>
            </a>
            <nav class="main-nav">
                <a href="index.html">首页</a>
                <a href="articles.html">文章</a>
                <a href="admin.html">管理</a>
            </nav>
        </div>
    </header>

    <main class="container article-container">
        <article class="article-detail">
            <header class="article-header">
                <h1 class="article-title">{title}</h1>
                <div class="article-meta">
                    <span class="article-date">发布时间：{date}</span>
                    <span class="article-source">来源：{source}</span>
                </div>
                <div class="article-keywords">
                    {''.join(f'<span class="keyword-tag">{kw}</span>' for kw in article.get('keywords', []))}
                </div>
            </header>

            <div class="article-content">
                {content}
            </div>

            <footer class="article-footer">
                <div class="article-tags">
                    <strong>相关标签：</strong>
                    {', '.join(article.get('keywords', []))}
                </div>
                <div class="disclaimer">
                    <strong>免责声明：</strong>本文仅供学习交流，不构成任何投资建议。交易有风险，入市需谨慎。
                </div>
            </footer>
        </article>

        <aside class="article-sidebar">
            <div class="sidebar-widget">
                <h3>关于谷比算力</h3>
                <p>专注区块链技术、量化交易策略与MT5/EA自动化交易的专业平台。</p>
            </div>
            <div class="sidebar-widget">
                <h3>热门标签</h3>
                <div class="tag-cloud">
                    <span class="keyword-tag">BTC</span>
                    <span class="keyword-tag">ETH</span>
                    <span class="keyword-tag">黄金XAUUSD</span>
                    <span class="keyword-tag">外汇</span>
                    <span class="keyword-tag">MT5</span>
                    <span class="keyword-tag">EA交易</span>
                    <span class="keyword-tag">技术分析</span>
                    <span class="keyword-tag">交易策略</span>
                </div>
            </div>
            <div class="sidebar-widget">
                <h3>关注我们</h3>
                <p>Telegram: <a href="https://t.me/gubutdata" target="_blank">@gubutdata</a></p>
                <p>Twitter/X: <a href="https://x.com/gubutdata" target="_blank">@gubutdata</a></p>
            </div>
        </aside>
    </main>

    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2025 谷比算力 gubut.com All Rights Reserved.</p>
            <p><a href="privacy.html">隐私政策</a> | <a href="terms.html">服务条款</a></p>
        </div>
    </footer>

    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "{title}",
        "datePublished": "{date.replace('/', '-')}",
        "author": {{
            "@type": "Organization",
            "name": "谷比算力"
        }},
        "publisher": {{
            "@type": "Organization",
            "name": "谷比算力",
            "logo": {{
                "@type": "ImageObject",
                "url": "https://www.gubut.com/img/logo.png"
            }}
        }},
        "mainEntityOfPage": {{
            "@type": "WebPage",
            "@id": "{canonical_url}"
        }},
        "keywords": "{keywords}",
        "description": "{description}"
    }}
    </script>
</body>
</html>"""
    
    return html, canonical_url


def update_sitemap(sitemap_content, new_url, lastmod_date):
    """向sitemap.xml添加新URL"""
    new_entry = f"""  <url>
    <loc>{new_url}</loc>
    <lastmod>{lastmod_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>"""
    
    # 替换最后的 </urlset> 标签
    if '</urlset>' in sitemap_content:
        updated = sitemap_content.replace('</urlset>', new_entry)
        return updated
    else:
        # 如果没有urlset，创建新的
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{new_entry}"""


def main():
    print("=" * 60)
    print("文章发布流程启动")
    print("=" * 60)
    
    # 1. 读取本地文章
    print("\n[步骤1] 读取本地 ai_article.json...")
    if not os.path.exists(AI_ARTICLE_PATH):
        print(f"❌ 错误: {AI_ARTICLE_PATH} 不存在!")
        sys.exit(1)
    
    with open(AI_ARTICLE_PATH, 'r', encoding='utf-8') as f:
        article = json.load(f)
    
    print(f"  标题: {article['title']}")
    print(f"  ID: {article['id']}")
    print(f"  日期: {article['date']}")
    print(f"  内容长度: {len(article['content'])} 字符")
    
    # 验证JSON
    print("\n[步骤2] 验证文章JSON格式...")
    try:
        with open(AI_ARTICLE_PATH, 'r', encoding='utf-8') as f:
            json.load(f)
        print("  ✅ JSON格式合法")
    except Exception as e:
        print(f"  ❌ JSON格式错误: {e}")
        sys.exit(1)
    
    # 2. 上传文章JSON到远程
    print("\n[步骤3] 上传 ai_article.json 到远程服务器...")
    if not upload_file(AI_ARTICLE_PATH, REMOTE_AI_ARTICLE):
        print("  ❌ 上传失败")
        sys.exit(1)
    
    # 3. 生成文章HTML页面
    print("\n[步骤4] 生成独立文章HTML页面...")
    article_html, article_url = generate_article_html(article)
    
    article_filename = f"article-{article['id']}.html"
    article_local_path = f"/workspace/new/{article_filename}"
    article_remote_path = f"{REMOTE_DIR}/{article_filename}"
    
    # 确保new目录存在
    os.makedirs("/workspace/new", exist_ok=True)
    
    with open(article_local_path, 'w', encoding='utf-8') as f:
        f.write(article_html)
    print(f"  ✅ 文章页面已生成: {article_local_path}")
    print(f"  ✅ 文章URL: {article_url}")
    
    # 上传文章页面
    print("\n[步骤5] 上传文章页面到远程...")
    if not upload_file(article_local_path, article_remote_path):
        print("  ❌ 文章页面上传失败")
        sys.exit(1)
    
    # 4. 追加文章到 articles.json
    print("\n[步骤6] 追加文章到 articles.json...")
    
    # 读取远程articles.json
    articles_json_content = run_remote(f"cat {REMOTE_ARTICLES_JSON}")
    try:
        all_articles = json.loads(articles_json_content) if articles_json_content.strip() else []
    except:
        all_articles = []
    print(f"  远程现有文章数: {len(all_articles)}")
    
    # 检查是否已发布
    existing_ids = {a.get('id') for a in all_articles}
    if article['id'] in existing_ids:
        print("  ⚠️  该文章已在articles.json中，跳过追加")
    else:
        # 新文章放最前面
        all_articles.insert(0, article)
        
        # 保存本地articles.json（同步）
        with open("/workspace/articles.json", 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
        # 上传到远程
        if upload_file("/workspace/articles.json", REMOTE_ARTICLES_JSON):
            print(f"  ✅ articles.json 已更新，当前共 {len(all_articles)} 篇")
        else:
            print("  ❌ articles.json 上传失败")
            sys.exit(1)
    
    # 5. 更新 sitemap.xml
    print("\n[步骤7] 更新 sitemap.xml...")
    
    sitemap_content = run_remote(f"cat {REMOTE_SITEMAP}")
    lastmod = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')
    
    # 检查URL是否已在sitemap中
    if article_url in sitemap_content:
        print("  ⚠️  URL已在sitemap中，跳过更新")
    else:
        updated_sitemap = update_sitemap(sitemap_content, article_url, lastmod)
        
        with open("/workspace/sitemap.xml", 'w', encoding='utf-8') as f:
            f.write(updated_sitemap)
        
        if upload_file("/workspace/sitemap.xml", REMOTE_SITEMAP):
            print("  ✅ sitemap.xml 已更新")
        else:
            print("  ❌ sitemap.xml 上传失败")
            sys.exit(1)
    
    # 6. 验证
    print("\n[步骤8] 远程验证...")
    
    aid = str(article['id'])
    
    # 验证文章页面存在
    check_html = run_remote(f"ls -la {article_remote_path}")
    if article_filename in check_html:
        print("  ✅ 文章HTML页面存在")
    else:
        print("  ❌ 文章HTML页面未找到")
    
    # 验证articles.json包含新文章 - 用grep简化检查
    check_articles = run_remote(f"grep -c '\"id\": {aid}' {REMOTE_ARTICLES_JSON}")
    if check_articles.strip() and int(check_articles.strip()) > 0:
        print("  ✅ articles.json 包含新文章")
    else:
        print("  ❌ articles.json 不包含新文章")
    
    # 验证sitemap
    grep_pattern = f"article-{aid}"
    check_sitemap = run_remote(f"grep -c '{grep_pattern}' {REMOTE_SITEMAP}")
    if check_sitemap.strip() and int(check_sitemap.strip()) > 0:
        print("  ✅ sitemap.xml 包含新URL")
    else:
        print("  ❌ sitemap.xml 不包含新URL")
    
    # 完成
    word_count = len(re.sub(r'<[^>]+>', '', article['content']))
    
    print("\n" + "=" * 60)
    print("🎉 发布完成!")
    print("=" * 60)
    print(f"  文章标题: {article['title']}")
    print(f"  文章URL:  {article_url}")
    print(f"  正文字数: {word_count} 字")
    print(f"  发布时间: {article['date']}")
    print("=" * 60)
    
    return article['title'], article_url, word_count


if __name__ == "__main__":
    main()
