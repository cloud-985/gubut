// _publish_ai.js - 发布 /www/wwwroot/gubut/ai_article.json 到 gubut.com
//
// 流程 (镜像 auto-publish.js 的 publishArticle + buildArticleHtml + updateSitemap):
//   1. 读取 ai_article.json
//   2. 读取 articles.json, 去重后 unshift 到顶部
//   3. 写回 articles.json
//   4. 生成 new/article-{id}.html (含完整 SEO: title/keywords/description/canonical/OG/Twitter/JSON-LD)
//   5. 更新 sitemap.xml
//   6. 追加到 .published-articles.json
//   7. chown www:www 修复权限
//
// 用法: node _publish_ai.js

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SITE_DIR = '/www/wwwroot/gubut';
const SITE_DOMAIN = 'https://www.gubut.com';
const AI_FILE = path.join(SITE_DIR, 'ai_article.json');
const ARTICLES_JSON = path.join(SITE_DIR, 'articles.json');
const PUBLISHED_LOG = path.join(SITE_DIR, '.published-articles.json');
const NEW_DIR = path.join(SITE_DIR, 'new');

function log(msg, type) {
  type = type || 'INFO';
  console.log('[' + type + '] ' + msg);
}

function buildArticleHtml(article) {
  const articleUrl = SITE_DOMAIN + '/new/article-' + article.id + '.html';
  const desc = (String(article.content || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').substring(0, 160)).trim();
  const datePublished = new Date(Number(article.id)).toISOString();

  // 关键词: 优先使用文章自带 keywords, 否则用站点默认
  const kw = Array.isArray(article.keywords) && article.keywords.length > 0
    ? article.keywords.join(', ')
    : '区块链策略开发, 量化交易策略, MT5, EA策略, 行情分析, 交易策略, 技术分析, 自动化交易';

  const websiteSchema = JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: '谷比算力',
    alternateName: 'gubut',
    url: SITE_DOMAIN + '/',
  });
  const articleSchema = JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: article.title,
    description: desc,
    datePublished: datePublished,
    dateModified: datePublished,
    mainEntityOfPage: { '@type': 'WebPage', '@id': articleUrl },
    image: SITE_DOMAIN + '/img/gubut.jpg',
    author: { '@type': 'Organization', name: '谷比算力' },
    publisher: {
      '@type': 'Organization',
      name: '谷比算力',
      logo: { '@type': 'ImageObject', url: SITE_DOMAIN + '/img/logo.png' },
    },
    keywords: Array.isArray(article.keywords) ? article.keywords.join(', ') : kw,
  });

  return '<!DOCTYPE html>\n<html lang="zh">\n<head>\n' +
    '    <meta charset="UTF-8">\n' +
    '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n' +
    '    <meta name="google-site-verification" content="FVQ6oEo6VtJ2YyT-BSgoX5-s43MPeuA3uPlVu5kJKw4" />\n\n' +
    '    <link rel="shortcut icon" href="../favicon.ico" type="image/x-icon">\n' +
    '    <title>' + article.title + ' - 谷比算力</title>\n' +
    '    <meta name="keywords" content="' + kw + '">\n' +
    '    <meta name="description" content="' + desc + '">\n\n' +
    '    <!-- Google Analytics 4 -->\n' +
    '    <script async src="https://www.googletagmanager.com/gtag/js?id=G-0HHCWGLR3N"></script>\n' +
    '    <script>\n' +
    '      window.dataLayer = window.dataLayer || [];\n' +
    '      function gtag(){dataLayer.push(arguments);}\n' +
    "      gtag('js', new Date());\n" +
    "      gtag('config', 'G-0HHCWGLR3N', { 'anonymize_ip': true });\n" +
    '    </script>\n\n' +
    '    <link rel="canonical" href="' + articleUrl + '" />\n\n' +
    '    <!-- Open Graph -->\n' +
    '    <meta property="og:type" content="article" />\n' +
    '    <meta property="og:url" content="' + articleUrl + '" />\n' +
    '    <meta property="og:title" content="' + article.title + '" />\n' +
    '    <meta property="og:description" content="' + desc + '" />\n' +
    '    <meta property="og:site_name" content="谷比算力" />\n' +
    '    <meta property="og:locale" content="zh_CN" />\n' +
    '    <meta property="og:image" content="' + SITE_DOMAIN + '/img/gubut.jpg" />\n\n' +
    '    <!-- Twitter Card -->\n' +
    '    <meta name="twitter:card" content="summary_large_image" />\n' +
    '    <meta name="twitter:title" content="' + article.title + '" />\n' +
    '    <meta name="twitter:description" content="' + desc + '" />\n' +
    '    <meta name="twitter:image" content="' + SITE_DOMAIN + '/img/gubut.jpg" />\n\n' +
    '    <!-- 引入Font Awesome -->\n' +
    '    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">\n' +
    '    <!-- 引入Tailwind CSS -->\n' +
    '    <script src="https://cdn.tailwindcss.com"></script>\n' +
    '    <!-- 引入Chart.js -->\n' +
    '    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n' +
    '    <!-- 引入样式文件 -->\n' +
    '    <link rel="stylesheet" href="../styles.css">\n' +
    '    <!-- 引入语言切换组件 -->\n' +
    '    <script src="../lang.js"></script>\n' +
    '    <script>\n' +
    '        tailwind.config = {\n' +
    '            theme: {\n' +
    '                extend: {\n' +
    '                    colors: {\n' +
    "                        primary: '#4F46E5',\n" +
    "                        secondary: '#10B981',\n" +
    "                        dark: '#111827',\n" +
    "                        light: '#F9FAFB'\n" +
    '                    },\n' +
    "                    fontFamily: { inter: ['Inter', 'system-ui', 'sans-serif'] }\n" +
    '                }\n' +
    '            }\n' +
    '        }\n' +
    '    </script>\n' +
    '    <!-- 站点名称结构化数据 -->\n' +
    '    <script type="application/ld+json">' + websiteSchema + '</script>\n' +
    '    <!-- 文章结构化数据 -->\n' +
    '    <script type="application/ld+json">' + articleSchema + '</script>\n' +
    '</head>\n<body>\n' +
    '    <div id="navbar-placeholder"></div>\n\n' +
    '    <div class="article-container">\n' +
    '        <article class="article-content">\n' +
    '            <h1>' + article.title + '</h1>\n' +
    '            <div class="article-meta">\n' +
    '                <span data-lang="zh">发布于: </span><span data-lang="en" class="hidden-lang">Published: </span>' + article.date + '\n' +
    '            </div>\n' +
    '            <div class="article-body">\n' +
    '                ' + article.content + '\n' +
    '            </div>\n\n' +
    '            <div class="related-articles">\n' +
    '                <h3>更多文章</h3>\n' +
    '                <div id="related-articles-list">\n' +
    '                    <p>加载中...</p>\n' +
    '                </div>\n' +
    '                <div class="all-articles-link">\n' +
    '                    <a href="../articles.html">查看所有文章 →</a>\n' +
    '                </div>\n' +
    '            </div>\n' +
    '        </article>\n' +
    '    </div>\n\n' +
    '    <!-- 数据信号服务板块 -->\n' +
    '    <section class="py-8 min-h-[20vh] flex items-center justify-center bg-gradient-to-br from-blue-900 via-blue-800 to-purple-700 text-white">\n' +
    '        <div class="container mx-auto px-2 sm:px-6 lg:px-8 w-full">\n' +
    '            <div class="text-center max-w-3xl mx-auto mb-16">\n' +
    '                <h2 class="text-[clamp(1.5rem,3vw,2.5rem)] font-bold mb-4">数据信号服务</h2>\n' +
    '                <p class="text-blue-100 text-lg">快人一步的行情数据，让你在别人还没反应时，就已经进场</p>\n' +
    '            </div>\n' +
    '            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 justify-items-center">\n' +
    '                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">\n' +
    '                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">🔔</div>\n' +
    '                    <h3 class="text-xl font-bold mb-3 text-center">新币上线提醒</h3>\n' +
    '                    <p class="text-blue-100 text-center">第一时间获取新币上线信息，抢占先机</p>\n' +
    '                </div>\n' +
    '                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">\n' +
    '                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">🚀</div>\n' +
    '                    <h3 class="text-xl font-bold mb-3 text-center">市场异动推送</h3>\n' +
    '                    <p class="text-blue-100 text-center">实时推送资金流异常、盘口深度变化等关键信号</p>\n' +
    '                </div>\n' +
    '                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">\n' +
    '                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">💎</div>\n' +
    '                    <h3 class="text-xl font-bold mb-3 text-center">VIP社群服务</h3>\n' +
    '                    <p class="text-blue-100 text-center">加入专属社群，获取全部信号和深度指标</p>\n' +
    '                </div>\n' +
    '            </div>\n' +
    '            <div class="mt-16 text-center">\n' +
    '                <a href="https://t.me/mevjk_bot" class="inline-block bg-white hover:bg-blue-50 text-blue-900 font-bold py-4 px-8 rounded-full transition-all duration-300 shadow-lg shadow-blue-400/20 hover:shadow-xl hover:shadow-blue-400/30 transform hover:-translate-y-1" target="_blank">免费获取信号</a>\n' +
    '            </div>\n' +
    '        </div>\n' +
    '    </section>\n\n' +
    '    <div id="social-floating-placeholder"></div>\n' +
    '    <div id="footer-placeholder"></div>\n' +
    '    <div id="mobile-navbar-placeholder"></div>\n\n' +
    '    <script src="../js/components.js"></script>\n' +
    '    <script>\n' +
    "        document.addEventListener('DOMContentLoaded', function() {\n" +
    '            loadRelatedArticles();\n' +
    '        });\n' +
    '        async function loadRelatedArticles() {\n' +
    "            const list = document.getElementById('related-articles-list');\n" +
    '            try {\n' +
    "                const response = await fetch('../articles.json');\n" +
    '                if (!response.ok) throw new Error(\'HTTP \' + response.status);\n' +
    '                const articles = await response.json();\n' +
    '                const currentUrl = window.location.href;\n' +
    '                const match = currentUrl.match(/article-(\\d+)\\.html/);\n' +
    '                const currentId = match ? match[1] : null;\n' +
    '                const related = articles.filter(a => a.id != currentId).map(a => ({\n' +
    '                    id: a.id, title: a.title, date: a.date || \'\', url: \'../new/article-\' + a.id + \'.html\'\n' +
    '                }));\n' +
    '                related.sort((a, b) => new Date(b.date) - new Date(a.date));\n' +
    '                list.innerHTML = related.slice(0, 5).map(a =>\n' +
    '                    \'<div class="related-article-item"><a href="\' + a.url + \'">\' + a.title + \'</a><span class="article-date">\' + (a.date || \'\') + \'</span></div>\'\n' +
    '                ).join(\'\') || \'<p>暂无其他文章</p>\';\n' +
    '            } catch (e) {\n' +
    '                list.innerHTML = \'<p>加载失败</p>\';\n' +
    '            }\n' +
    '        }\n' +
    '    </script>\n' +
    '</body>\n</html>';
}

function updateSitemap(articles) {
  const today = new Date().toISOString().split('T')[0];
  const publicPages = [
    [SITE_DOMAIN + '/', '1.0', 'daily'],
    [SITE_DOMAIN + '/articles.html', '0.9', 'daily'],
    [SITE_DOMAIN + '/strategy.html', '0.8', 'weekly'],
    [SITE_DOMAIN + '/contact.html', '0.7', 'monthly'],
    [SITE_DOMAIN + '/terms.html', '0.5', 'monthly'],
    [SITE_DOMAIN + '/privacy.html', '0.5', 'monthly'],
  ];

  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
  for (const p of publicPages) {
    xml += '  <url>\n    <loc>' + p[0] + '</loc>\n    <lastmod>' + today + '</lastmod>\n    <changefreq>' + p[2] + '</changefreq>\n    <priority>' + p[1] + '</priority>\n  </url>\n';
  }
  for (const a of articles) {
    xml += '  <url>\n    <loc>' + SITE_DOMAIN + '/new/article-' + a.id + '.html</loc>\n    <lastmod>' + today + '</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n';
  }
  xml += '</urlset>\n';
  fs.writeFileSync(path.join(SITE_DIR, 'sitemap.xml'), xml);
  log('sitemap.xml 已更新 (' + (publicPages.length + articles.length) + ' 个URL)', 'OK');
}

function main() {
  log('='.repeat(60));
  log('Gubut AI 文章发布任务启动');
  log('时间: ' + new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' }));
  log('='.repeat(60));

  // 1. 读取 ai_article.json
  if (!fs.existsSync(AI_FILE)) {
    log('ai_article.json 不存在, 退出', 'ERR');
    process.exit(2);
  }
  const article = JSON.parse(fs.readFileSync(AI_FILE, 'utf8'));
  log('读取 ai_article.json: id=' + article.id + ', title=' + article.title);

  // 必填字段检查
  for (const k of ['id', 'title', 'date', 'content']) {
    if (article[k] == null) {
      log('ai_article.json 缺少必填字段: ' + k, 'ERR');
      process.exit(3);
    }
  }

  // 2. 读取 articles.json 并去重
  let articles = [];
  try {
    articles = JSON.parse(fs.readFileSync(ARTICLES_JSON, 'utf8'));
  } catch (e) {
    log('articles.json 读取失败, 使用空数组: ' + e.message, 'WARN');
  }
  if (articles.some(a => Number(a.id) === Number(article.id))) {
    log('文章 id=' + article.id + ' 已存在于 articles.json, 跳过追加', 'WARN');
  } else {
    articles.unshift(article);
    fs.writeFileSync(ARTICLES_JSON, JSON.stringify(articles, null, 2));
    log('已追加到 articles.json (共 ' + articles.length + ' 篇)', 'OK');
  }

  // 3. 生成文章页 (含完整 SEO)
  if (!fs.existsSync(NEW_DIR)) fs.mkdirSync(NEW_DIR, { recursive: true });
  const htmlPath = path.join(NEW_DIR, 'article-' + article.id + '.html');
  fs.writeFileSync(htmlPath, buildArticleHtml(article));
  log('已生成文章页: ' + htmlPath, 'OK');

  // 4. 更新 sitemap.xml
  updateSitemap(articles);

  // 5. 追加到 .published-articles.json
  let published = [];
  try {
    published = JSON.parse(fs.readFileSync(PUBLISHED_LOG, 'utf8'));
  } catch (e) {}
  if (!published.some(p => p && Number(p.articleId) === Number(article.id))) {
    published.push({
      titleKey: String(article.title).substring(0, 30).toLowerCase(),
      publishedAt: new Date().toISOString(),
      articleId: article.id,
      source: article.source || '',
    });
    fs.writeFileSync(PUBLISHED_LOG, JSON.stringify(published, null, 2));
    log('已记录到 .published-articles.json', 'OK');
  } else {
    log('该 id 已在 .published-articles.json 中, 跳过记录', 'WARN');
  }

  // 6. 修复权限
  try {
    execSync('chown www:www ' + htmlPath + ' ' + ARTICLES_JSON + ' ' + PUBLISHED_LOG + ' ' + path.join(SITE_DIR, 'sitemap.xml') + ' ' + AI_FILE + ' 2>/dev/null || true');
    execSync('chown -R www:www ' + NEW_DIR + ' 2>/dev/null || true');
    log('权限已修复 (www:www)', 'OK');
  } catch (e) {
    log('权限修复失败(非致命): ' + e.message, 'WARN');
  }

  log('='.repeat(60));
  log('发布完成!');
  log('文章 URL: ' + SITE_DOMAIN + '/new/article-' + article.id + '.html', 'OK');
  log('='.repeat(60));
}

try {
  main();
} catch (e) {
  log('发布失败: ' + e.message, 'ERR');
  console.error(e.stack);
  process.exit(1);
}
