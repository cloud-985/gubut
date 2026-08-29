"""
上传并发布文章：
- 读取 /workspace/ai_article.json
- 生成文章HTML页面（含完整SEO标签）
- 追加到 articles.json
- 更新 sitemap.xml
- 上传所有文件到远程服务器
"""
import json
import os
import sys
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ssh_tunnel import (
    REMOTE_DIR,
    read_remote_json,
    write_remote_json,
    upload_local_to_remote,
    read_remote_file,
    write_remote_file,
    run_remote
)

WORKSPACE = "/workspace"


def extract_text_from_html(html):
    """提取纯文本（用于articles.json摘要）"""
    text = re.sub(r"<[^>]*>", "", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_article_html(article):
    """根据 generate-article.js 模板生成独立文章页"""
    keywords_str = "，".join(article.get("keywords", []))
    # 从正文生成描述（取前150字纯文本）
    plain_text = extract_text_from_html(article["content"])
    description = plain_text[:150] + ("..." if len(plain_text) > 150 else "")
    if len(description) < 50:
        description = "谷比算力 - 专注于区块链技术与量化交易策略的专业平台，提供MT5、EA自动化交易方案与技术分析。"

    article_id = article["id"]
    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="../favicon.ico" type="image/x-icon">
    <title>{article['title']} - 谷比算力</title>
    <meta name="keywords" content="{keywords_str}">
    <meta name="description" content="{description}">
    <!-- Open Graph -->
    <meta property="og:title" content="{article['title']} - 谷比算力">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://www.gubut.com/new/article-{article_id}.html">
    <meta property="og:site_name" content="谷比算力">
    <meta property="og:image" content="https://www.gubut.com/img/logo.png">
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{article['title']} - 谷比算力">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="https://www.gubut.com/img/logo.png">
    <!-- Canonical -->
    <link rel="canonical" href="https://www.gubut.com/new/article-{article_id}.html">
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="../styles.css">
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
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": {json.dumps(article['title'], ensure_ascii=False)},
      "description": {json.dumps(description, ensure_ascii=False)},
      "datePublished": "{article['date']}",
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
        "@id": "https://www.gubut.com/new/article-{article_id}.html"
      }},
      "image": "https://www.gubut.com/img/logo.png",
      "keywords": {json.dumps(keywords_str, ensure_ascii=False)}
    }}
    </script>
</head>
<body>
    <div id="navbar-placeholder"></div>
    <div class="article-container">
        <article class="article-content">
            <h1>{article['title']}</h1>
            <div class="article-meta">
                <span>发布于: </span>{article['date']}
            </div>
            <div class="article-body">
                {article['content']}
            </div>
            <div class="related-articles">
                <h3>更多文章</h3>
                <div id="related-articles-list">
                    <p>加载中...</p>
                </div>
                <div class="all-articles-link">
                    <a href="../articles.html">查看所有文章 &rarr;</a>
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
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">&#128276;</div>
                    <h3 class="text-xl font-bold mb-3 text-center">新币上线提醒</h3>
                    <p class="text-blue-100 text-center">第一时间获取新币上线信息，抢占先机</p>
                </div>
                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">&#128640;</div>
                    <h3 class="text-xl font-bold mb-3 text-center">市场异动推送</h3>
                    <p class="text-blue-100 text-center">实时推送资金流异常、盘口深度变化等关键信号</p>
                </div>
                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">&#128142;</div>
                    <h3 class="text-xl font-bold mb-3 text-center">VIP社群服务</h3>
                    <p class="text-blue-100 text-center">加入专属社群，获取全部信号和深度指标</p>
                </div>
            </div>
            <div class="mt-16 text-center">
                <a href="https://t.me/mevjk_bot" class="inline-block bg-white hover:bg-blue-50 text-blue-900 font-bold py-4 px-8 rounded-full transition-all duration-300 shadow-lg shadow-blue-400/20 hover:shadow-xl hover:shadow-blue-400/30 transform hover:-translate-y-1" target="_blank">
                    免费获取信号
                </a>
            </div>
        </div>
    </section>
    <div id="social-floating-placeholder"></div>
    <div id="footer-placeholder"></div>
    <div id="mobile-navbar-placeholder"></div>
    <script src="../js/components.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            loadRelatedArticles();
        }});
        async function loadRelatedArticles() {{
            const relatedArticlesList = document.getElementById('related-articles-list');
            try {{
                const response = await fetch('../articles.json');
                if (!response.ok) throw new Error('HTTP error! status: ' + response.status);
                const articles = await response.json();
                const currentUrl = window.location.href;
                const matchResult = currentUrl.match(/article-(\\d+)\\.html/);
                const currentArticleId = matchResult ? matchResult[1] : null;
                const relatedArticles = articles
                    .filter(article => article.id != currentArticleId)
                    .map(article => ({{
                        id: article.id,
                        title: article.title,
                        date: article.date || "",
                        url: "../new/article-" + article.id + ".html"
                    }}));
                relatedArticles.sort((a, b) => {{
                    if (a.date && b.date) return new Date(b.date) - new Date(a.date);
                    else if (a.date) return -1;
                    else if (b.date) return 1;
                    return 0;
                }});
                displayRelatedArticles(relatedArticles);
            }} catch (error) {{
                console.error('加载相关文章失败:', error);
                relatedArticlesList.innerHTML = '<p>加载相关文章失败</p>';
            }}
        }}
        function displayRelatedArticles(articles) {{
            const relatedArticlesList = document.getElementById('related-articles-list');
            if (!articles || articles.length === 0) {{
                relatedArticlesList.innerHTML = '<p>暂无相关文章</p>';
                return;
            }}
            const relatedArticles = articles.slice(0, 20);
            relatedArticlesList.innerHTML = '';
            relatedArticles.forEach(article => {{
                const relatedArticle = document.createElement('div');
                relatedArticle.className = 'related-article';
                let articleHTML = '<a href="' + article.url + '">' + escapeHtml(article.title) + '</a>';
                if (article.date) articleHTML += '<span class="related-article-date">' + article.date + '</span>';
                relatedArticle.innerHTML = articleHTML;
                relatedArticlesList.appendChild(relatedArticle);
            }});
        }}
        function escapeHtml(text) {{
            const map = {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}};
            return text.replace(/[&<>"']/g, function(m) {{ return map[m]; }});
        }}
    </script>
</body>
</html>"""
    return html


def build_sitemap(articles_list):
    """构建sitemap.xml"""
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [
        ("https://www.gubut.com/index.html", "daily", "1.0"),
        ("https://www.gubut.com/articles.html", "daily", "0.9"),
    ]
    for art in articles_list:
        aid = art["id"]
        urls.append((f"https://www.gubut.com/new/article-{aid}.html", "weekly", "0.8"))

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, freq, pri in urls:
        sitemap += f"    <url>\n"
        sitemap += f"        <loc>{loc}</loc>\n"
        sitemap += f"        <lastmod>{today}</lastmod>\n"
        sitemap += f"        <changefreq>{freq}</changefreq>\n"
        sitemap += f"        <priority>{pri}</priority>\n"
        sitemap += f"    </url>\n"
    sitemap += "</urlset>"
    return sitemap


def main():
    ai_path = f"{WORKSPACE}/ai_article.json"
    if not os.path.exists(ai_path):
        print(f"ERROR: {ai_path} 不存在")
        sys.exit(1)

    with open(ai_path, "r", encoding="utf-8") as f:
        new_article = json.load(f)

    article_id = new_article["id"]
    print(f"[{datetime.now()}] 开始发布文章: id={article_id}")
    print(f"  标题: {new_article['title']}")

    # 1. 生成文章HTML
    local_new_dir = f"{WORKSPACE}/new"
    os.makedirs(local_new_dir, exist_ok=True)
    article_html = build_article_html(new_article)
    article_file_name = f"article-{article_id}.html"
    local_article_path = f"{local_new_dir}/{article_file_name}"
    with open(local_article_path, "w", encoding="utf-8") as f:
        f.write(article_html)
    print(f"  文章页已生成: {local_article_path}")

    # 2. 读取远程 articles.json，追加新文章（本地articles.json作为参考）
    remote_articles_path = f"{REMOTE_DIR}/articles.json"
    try:
        articles = read_remote_json(remote_articles_path)
    except Exception:
        # 回退：读取本地
        with open(f"{WORKSPACE}/articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)

    # 构建 articles.json 条目（纯文本内容）
    articles_entry = {
        "id": new_article["id"],
        "title": new_article["title"],
        "date": new_article["date"],
        "content": extract_text_from_html(new_article["content"])
    }
    # 去重
    articles = [a for a in articles if str(a.get("id")) != str(article_id)]
    articles.insert(0, articles_entry)  # 新文章在前面

    # 保存本地 articles.json
    with open(f"{WORKSPACE}/articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    # 3. 生成 sitemap.xml
    sitemap_xml = build_sitemap(articles)
    with open(f"{WORKSPACE}/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    # 4. 上传文件到远程服务器
    print("  上传文件到远程服务器...")

    # 上传 articles.json
    write_remote_json(remote_articles_path, articles)
    print(f"    - articles.json 更新（共{len(articles)}篇）")

    # 上传文章HTML
    upload_local_to_remote(local_article_path, f"{REMOTE_DIR}/new/{article_file_name}")
    print(f"    - new/{article_file_name} 上传成功")

    # 上传 sitemap.xml
    write_remote_file(f"{REMOTE_DIR}/sitemap.xml", sitemap_xml)
    print(f"    - sitemap.xml 更新成功")

    # 确保远程 new 目录权限
    run_remote(f"chmod -R 755 {REMOTE_DIR}/new && chmod 644 {REMOTE_DIR}/articles.json {REMOTE_DIR}/sitemap.xml {REMOTE_DIR}/new/{article_file_name}")

    article_url = f"https://www.gubut.com/new/article-{article_id}.html"
    print(f"\n{'='*60}")
    print(f"发布成功！")
    print(f"标题: {new_article['title']}")
    print(f"URL:  {article_url}")
    word_count = len(extract_text_from_html(new_article["content"]))
    print(f"字数:  {word_count} 字")
    print(f"{'='*60}")
    return article_url


if __name__ == "__main__":
    main()
