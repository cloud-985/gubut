# -*- coding: utf-8 -*-
"""
发布文章：
1. 读取 /workspace/ai_article.json
2. 生成带完整 SEO 标签的文章页 HTML
3. 上传文章页到服务器 new/article-{id}.html
4. 追加文章到服务器 articles.json
5. 更新服务器 sitemap.xml
"""
import json
import os
import re
import tempfile

import ssh_tunnel

REMOTE_DIR = "/www/wwwroot/gubut"
LOCAL_ARTICLE = "/workspace/ai_article.json"


def strip_html(html):
    text = re.sub(r"<[^>]+>", "", html)
    return re.sub(r"\s+", " ", text).strip()


def make_description(content, limit=120):
    text = strip_html(content)
    if len(text) > limit:
        return text[:limit].rstrip("，。；：、") + "……"
    return text


def make_article_html(article):
    title = article["title"]
    keywords = ", ".join(article["keywords"])
    description = make_description(article["content"])
    date = article["date"]
    content = article["content"]

    # 处理图片路径（与 build.js 保持一致）
    processed = re.sub(r'<img\s+src="img/', '<img src="/img/', content)

    return """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="../favicon.ico" type="image/x-icon">
    <title>{title} - 谷比算力</title>
    <meta name="keywords" content="{keywords}">
    <meta name="description" content="{description}">
    <!-- 引入Font Awesome -->
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <!-- 引入Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- 引入Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- 引入样式文件 -->
    <link rel="stylesheet" href="../styles.css">
    <!-- 引入语言切换组件 -->
    <script src="../lang.js"></script>
        <!-- 自定义配置 -->
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
    <!-- 导航栏占位符 -->
    <div id="navbar-placeholder"></div>

    <div class="article-container">
        <article class="article-content">
            <h1>{title}</h1>
            <div class="article-meta">
                <span data-lang="zh">发布于: </span><span data-lang="en" class="hidden-lang">Published: </span>{date}
            </div>
            <div class="article-body">
                {content}
            </div>

            <div class="related-articles">
                <h3>更多文章</h3>
                <div id="related-articles-list">
                <!-- 相关文章将通过JavaScript动态加载 -->
                    <p>加载中...</p>
                </div>
                <div class="all-articles-link">
                    <a href="../articles.html">查看所有文章 →</a>
                </div>
            </div>
        </article>
    </div>

    <!-- 数据信号服务板块 -->
    <section class="py-8 min-h-[20vh] flex items-center justify-center bg-gradient-to-br from-blue-900 via-blue-800 to-purple-700 text-white">
        <div class="container mx-auto px-2 sm:px-6 lg:px-8 w-full">
            <div class="text-center max-w-3xl mx-auto mb-16">
                <h2 class="text-[clamp(1.5rem,3vw,2.5rem)] font-bold mb-4" data-lang-key="signals.title">
                    数据信号服务
                </h2>
                <p class="text-blue-100 text-lg" data-lang-key="signals.subtitle">
                    快人一步的行情数据，让你在别人还没反应时，就已经进场
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 justify-items-center">
                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">🔔</div>
                    <h3 class="text-xl font-bold mb-3 text-center" data-lang-key="signal.new.title">
                        新币上线提醒
                    </h3>
                    <p class="text-blue-100 text-center" data-lang-key="signal.new.desc">
                        第一时间获取新币上线信息，抢占先机
                    </p>
                </div>

                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">🚀</div>
                    <h3 class="text-xl font-bold mb-3 text-center" data-lang-key="signal.market.title">
                        市场异动推送
                    </h3>
                    <p class="text-blue-100 text-center" data-lang-key="signal.market.desc">
                        实时推送资金流异常、盘口深度变化等关键信号
                    </p>
                </div>

                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">💎</div>
                    <h3 class="text-xl font-bold mb-3 text-center" data-lang-key="signal.vip.title">
                        VIP社群服务
                    </h3>
                    <p class="text-blue-100 text-center" data-lang-key="signal.vip.desc">
                        加入专属社群，获取全部信号和深度指标
                    </p>
                </div>
            </div>

            <div class="mt-16 text-center">
                <a href="https://t.me/mevjk_bot" class="inline-block bg-white hover:bg-blue-50 text-blue-900 font-bold py-4 px-8 rounded-full transition-all duration-300 shadow-lg shadow-blue-400/20 hover:shadow-xl hover:shadow-blue-400/30 transform hover:-translate-y-1" target="_blank" data-lang-key="signal.btn">
                    免费获取信号
                </a>
            </div>
        </div>
    </section>

    <!-- 悬浮社交按钮占位符 -->
    <div id="social-floating-placeholder"></div>

    <!-- 底部占位符 -->
    <div id="footer-placeholder"></div>

    <!-- 移动端底部导航栏占位符 -->
    <div id="mobile-navbar-placeholder"></div>

    <!-- 引入组件加载脚本 -->
    <script src="../js/components.js"></script>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            loadRelatedArticles();
        }});

        async function loadRelatedArticles() {{
            const relatedArticlesList = document.getElementById('related-articles-list');

            try {{
                const response = await fetch('../articles.json');
                if (!response.ok) {{
                    throw new Error('HTTP error! status: ' + response.status);
                }}

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
                    if (a.date && b.date) {{
                        return new Date(b.date) - new Date(a.date);
                    }} else if (a.date) {{
                        return -1;
                    }} else if (b.date) {{
                        return 1;
                    }} else {{
                        return 0;
                    }}
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
                if (article.date) {{
                    articleHTML += '<span class="related-article-date">' + article.date + '</span>';
                }}

                relatedArticle.innerHTML = articleHTML;
                relatedArticlesList.appendChild(relatedArticle);
            }});
        }}

        function escapeHtml(text) {{
            const map = {{
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            }};
            return text.replace(/[&<>"']/g, function(m) {{ return map[m]; }});
        }}
    </script>
</body>
</html>""".format(title=title, keywords=keywords, description=description, date=date, content=processed)


def _write_tmp_and_put(content, remote_path):
    fd, tmp = tempfile.mkstemp(suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        ssh_tunnel.put_file(tmp, remote_path)
    finally:
        os.remove(tmp)


def main():
    with open(LOCAL_ARTICLE, "r", encoding="utf-8") as f:
        article = json.load(f)

    article_id = article["id"]
    print("发布文章 ID:", article_id)
    print("标题:", article["title"])

    # 1. 生成并上传文章页
    html = make_article_html(article)
    html_path = "{}/new/article-{}.html".format(REMOTE_DIR, article_id)
    _write_tmp_and_put(html, html_path)
    print("✓ 文章页已上传:", html_path)

    # 2. 追加到 articles.json
    articles_json_path = "{}/articles.json".format(REMOTE_DIR)
    raw = ssh_tunnel.read_file(articles_json_path)
    articles = json.loads(raw) if raw.strip() else []
    entry = {
        "id": article_id,
        "title": article["title"],
        "date": article["date"],
        "source": article["source"],
        "keywords": article["keywords"],
        "content": article["content"],
    }
    articles = [a for a in articles if a.get("id") != article_id]
    articles.insert(0, entry)
    _write_tmp_and_put(json.dumps(articles, ensure_ascii=False, indent=2), articles_json_path)
    print("✓ articles.json 已更新，当前共 {} 篇".format(len(articles)))

    # 3. 更新 sitemap.xml
    sitemap_path = "{}/sitemap.xml".format(REMOTE_DIR)
    sitemap = ssh_tunnel.read_file(sitemap_path)
    article_url = "https://www.gubut.com/new/article-{}.html".format(article_id)
    if article_url in sitemap:
        print("✓ sitemap 已包含该 URL，跳过插入")
    else:
        lastmod = article["date"].split(" ")[0].replace("/", "-")
        new_url_block = (
            "    <url>\n"
            "        <loc>{}</loc>\n"
            "        <lastmod>{}</lastmod>\n"
            "        <changefreq>weekly</changefreq>\n"
            "        <priority>0.8</priority>\n"
            "    </url>\n"
        ).format(article_url, lastmod)
        if "</urlset>" in sitemap:
            sitemap = sitemap.replace("</urlset>", new_url_block + "</urlset>")
        else:
            sitemap = sitemap.rstrip() + "\n" + new_url_block + "</urlset>\n"
        _write_tmp_and_put(sitemap, sitemap_path)
        print("✓ sitemap.xml 已更新")

    # 4. 汇总
    plain = strip_html(article["content"])
    print("\n" + "=" * 50)
    print("发布完成")
    print("标题:", article["title"])
    print("URL:", article_url)
    print("字数(去HTML/空白):", len(re.sub(r"\\s+", "", plain)))


if __name__ == "__main__":
    main()
