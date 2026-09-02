#!/usr/bin/env python3
"""Publish the article from ai_article.json:
- Append to articles.json (full HTML, keep existing format convention)
- Generate article page with SEO tags
- Update sitemap.xml
- Upload to remote server
"""
import json
import os
import re
import sys
from datetime import date
import subprocess

import ssh_tunnel

WORKSPACE = "/workspace"
REMOTE_ROOT = "/www/wwwroot/gubut"


def strip_html(text):
    text = re.sub(r"<[^>]+>", "", text or "")
    text = re.sub(r"&[a-zA-Z]+;", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_description(content, max_len=160):
    """Extract first meaningful paragraph as SEO description."""
    plain = strip_html(content)
    if len(plain) <= max_len:
        return plain
    # Try to find sentence break
    for sep in ["。", "！", "？", ". ", "! ", "? "]:
        idx = plain.find(sep)
        if 30 <= idx <= max_len:
            return plain[: idx + len(sep)]
    return plain[:max_len] + "…"


def update_articles_json(article):
    path = os.path.join(WORKSPACE, "articles.json")
    with open(path, "r", encoding="utf-8") as f:
        articles = json.load(f)
    # Remove duplicate if any
    articles = [a for a in articles if str(a.get("id")) != str(article["id"])]
    entry = {
        "id": article["id"],
        "title": article["title"],
        "date": article["date"],
        "content": article["content"],  # full HTML (matches existing format)
    }
    articles.insert(0, entry)  # newest first
    with open(path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"✅ articles.json 已更新 (共 {len(articles)} 篇)")
    return articles


def generate_article_page(article):
    """Generate individual HTML article page with proper SEO tags."""
    title = article["title"]
    keywords_str = "，".join(article.get("keywords", []))
    default_kw = "区块链策略开发, 量化交易策略, 数据采集, 行情数据接口, K线数据, 交易所API, 策略回测, Web3数据, 区块链数据分析, 自动化交易"
    if not keywords_str:
        keywords_str = default_kw
    else:
        keywords_str = keywords_str + "，" + default_kw
    description = extract_description(article["content"])
    # Convert relative img/ paths to absolute
    processed_content = article["content"]
    processed_content = re.sub(r'<img\s+src="img/', '<img src="/img/', processed_content)

    article_html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="../favicon.ico" type="image/x-icon">
    <title>{title} - 谷比算力</title>
    <meta name="keywords" content="{keywords_str}">
    <meta name="description" content="{description}">
    <meta property="og:title" content="{title} - 谷比算力">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="谷比算力">
    <meta property="article:published_time" content="{article['date']}">
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="../styles.css">
    <script src="../lang.js"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        primary: '#4F46E5',
                        secondary: '#10B981',
                        dark: '#111827',
                        light: '#F9FAFB'
                    }},
                    fontFamily: {{
                        inter: ['Inter', 'system-ui', 'sans-serif'],
                    }},
                }}
            }}
        }}
    </script>
</head>
<body>
    <div id="navbar-placeholder"></div>
    <div class="article-container">
        <article class="article-content">
            <h1>{title}</h1>
            <div class="article-meta">
                <span>发布于: </span>{article['date']}
                <span style="margin-left:16px;">来源: </span>{article.get('source', '原创')}
            </div>
            <div class="article-body">
                {processed_content}
            </div>
            <div class="related-articles">
                <h3>更多文章</h3>
                <div id="related-articles-list"><p>加载中...</p></div>
                <div class="all-articles-link">
                    <a href="../articles.html">查看所有文章 →</a>
                </div>
            </div>
        </article>
    </div>
    <section class="py-8 min-h-[20vh] flex items-center justify-center bg-gradient-to-br from-blue-900 via-blue-800 to-purple-700 text-white">
        <div class="container mx-auto px-2 sm:px-6 lg:px-8 w-full">
            <div class="text-center max-w-3xl mx-auto mb-16">
                <h2 class="text-[clamp(1.5rem,3vw,2.5rem)] font-bold mb-4">数据信号服务</h2>
                <p class="text-blue-100 text-lg">快人一步的行情数据，让你在别人还没反应时，就已经进场</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 justify-items-center">
                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">🔔</div>
                    <h3 class="text-xl font-bold mb-3 text-center">新币上线提醒</h3>
                    <p class="text-blue-100 text-center">第一时间获取新币上线信息，抢占先机</p>
                </div>
                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">🚀</div>
                    <h3 class="text-xl font-bold mb-3 text-center">市场异动推送</h3>
                    <p class="text-blue-100 text-center">实时推送资金流异常、盘口深度变化等关键信号</p>
                </div>
                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">💎</div>
                    <h3 class="text-xl font-bold mb-3 text-center">VIP社群服务</h3>
                    <p class="text-blue-100 text-center">加入专属社群，获取全部信号和深度指标</p>
                </div>
            </div>
            <div class="mt-16 text-center">
                <a href="https://t.me/mevjk_bot" class="inline-block bg-white hover:bg-blue-50 text-blue-900 font-bold py-4 px-8 rounded-full transition-all duration-300 shadow-lg shadow-blue-400/20 hover:shadow-xl hover:shadow-blue-400/30 transform hover:-translate-y-1" target="_blank">免费获取信号</a>
            </div>
        </div>
    </section>
    <div id="social-floating-placeholder"></div>
    <div id="footer-placeholder"></div>
    <div id="mobile-navbar-placeholder"></div>
    <script src="../js/components.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{ loadRelatedArticles(); }});
        async function loadRelatedArticles() {{
            var el = document.getElementById('related-articles-list');
            try {{
                var r = await fetch('../articles.json');
                if (!r.ok) throw new Error('HTTP error! status: ' + r.status);
                var articles = await r.json();
                var currentId = (window.location.href.match(/article-(\\d+)\\.html/) || [])[1];
                var related = articles
                    .filter(function(a){{ return String(a.id) !== String(currentId); }})
                    .map(function(a){{ return {{id:a.id,title:a.title,date:a.date||'',url:'../new/article-'+a.id+'.html'}}; }});
                related.sort(function(a,b){{
                    if (a.date && b.date) return new Date(b.date)-new Date(a.date);
                    if (a.date) return -1; if (b.date) return 1; return 0;
                }});
                displayRelated(related.slice(0,20));
            }} catch(e) {{ console.error('加载失败:',e); el.innerHTML='<p>加载相关文章失败</p>'; }}
        }}
        function displayRelated(list) {{
            var el = document.getElementById('related-articles-list');
            if (!list || !list.length) {{ el.innerHTML='<p>暂无相关文章</p>'; return; }}
            el.innerHTML='';
            list.forEach(function(a){{
                var div=document.createElement('div'); div.className='related-article';
                var html='<a href="'+a.url+'">'+escapeHtml(a.title)+'</a>';
                if(a.date) html+='<span class="related-article-date">'+a.date+'</span>';
                div.innerHTML=html; el.appendChild(div);
            }});
        }}
        function escapeHtml(t){{return (t||'').replace(/[&<>"']/g,function(m){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[m];}});}}
    </script>
</body>
</html>
"""
    new_dir = os.path.join(WORKSPACE, "new")
    os.makedirs(new_dir, exist_ok=True)
    page_path = os.path.join(new_dir, f"article-{article['id']}.html")
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(article_html)
    print(f"✅ 文章页已生成: new/article-{article['id']}.html")
    return page_path


def update_sitemap(articles):
    """Generate sitemap.xml based on articles list."""
    today = date.today().isoformat()
    sitemap_path = os.path.join(WORKSPACE, "sitemap.xml")

    existing_urls = {}
    if os.path.exists(sitemap_path):
        with open(sitemap_path, "r", encoding="utf-8") as f:
            data = f.read()
        for m in re.finditer(
            r"<url>[\s\S]*?<loc>(.*?)<\/loc>[\s\S]*?<lastmod>(.*?)<\/lastmod>[\s\S]*?<\/url>",
            data,
        ):
            existing_urls[m.group(1)] = m.group(2)

    urls = [
        (
            "https://www.gubut.com/index.html",
            existing_urls.get("https://www.gubut.com/index.html", today),
            "daily",
            "1.0",
        ),
        (
            "https://www.gubut.com/articles.html",
            existing_urls.get("https://www.gubut.com/articles.html", today),
            "daily",
            "0.9",
        ),
    ]
    for a in articles:
        article_url = f"https://www.gubut.com/new/article-{a['id']}.html"
        lastmod = existing_urls.get(article_url, today)
        urls.append((article_url, lastmod, "weekly", "0.8"))

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, lastmod, freq, prio in urls:
        xml += "    <url>\n"
        xml += f"        <loc>{loc}</loc>\n"
        xml += f"        <lastmod>{lastmod}</lastmod>\n"
        xml += f"        <changefreq>{freq}</changefreq>\n"
        xml += f"        <priority>{prio}</priority>\n"
        xml += "    </url>\n"
    xml += "</urlset>"

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"✅ sitemap.xml 已更新 (共 {len(urls)} 个URL)")


def upload_to_server(article_id, page_path):
    """Upload updated files to remote server via ssh_tunnel."""
    print("🚀 上传到远程服务器...")

    ssh_tunnel.upload_file(
        os.path.join(WORKSPACE, "articles.json"),
        f"{REMOTE_ROOT}/articles.json",
    )
    print("   ☑ articles.json 上传完成")

    ssh_tunnel.upload_file(
        page_path,
        f"{REMOTE_ROOT}/new/article-{article_id}.html",
    )
    print(f"   ☑ article-{article_id}.html 上传完成")

    ssh_tunnel.upload_file(
        os.path.join(WORKSPACE, "sitemap.xml"),
        f"{REMOTE_ROOT}/sitemap.xml",
    )
    print("   ☑ sitemap.xml 上传完成")

    # Ensure proper permissions
    ssh_tunnel.run_remote(
        f"chown -R www:www {REMOTE_ROOT}/articles.json {REMOTE_ROOT}/sitemap.xml {REMOTE_ROOT}/new/article-{article_id}.html && "
        f"chmod 644 {REMOTE_ROOT}/articles.json {REMOTE_ROOT}/sitemap.xml {REMOTE_ROOT}/new/article-{article_id}.html"
    )
    print("   ☑ 文件权限已修正")


def main():
    ai_path = os.path.join(WORKSPACE, "ai_article.json")
    if not os.path.exists(ai_path):
        print("❌ 未找到 ai_article.json，请先执行 gen_article.py")
        sys.exit(1)

    with open(ai_path, "r", encoding="utf-8") as f:
        article = json.load(f)

    print(f"📝 准备发布: {article['title']}")
    print(f"   ID: {article['id']}  日期: {article['date']}")

    # 1. Update articles.json
    articles = update_articles_json(article)

    # 2. Generate article page
    page_path = generate_article_page(article)

    # 3. Update sitemap
    update_sitemap(articles)

    # 4. Upload
    upload_to_server(article["id"], page_path)

    article_url = f"https://www.gubut.com/new/article-{article['id']}.html"
    zh_count = len(re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', strip_html(article["content"])))
    print()
    print("🎉 发布成功!")
    print(f"   标题: {article['title']}")
    print(f"   URL:  {article_url}")
    print(f"   字数: ~{zh_count}")

    return article, article_url, zh_count


if __name__ == "__main__":
    main()
