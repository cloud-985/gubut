// 用于生成文章页面和网站地图的Node.js脚本
// 在实际部署环境中，这个脚本会在服务器端运行

const fs = require('fs');
const path = require('path');

// 确保new目录存在
const newDir = path.join(__dirname, 'new');
if (!fs.existsSync(newDir)) {
    fs.mkdirSync(newDir);
}

/**
 * 生成独立的文章HTML页面
 * @param {Object} article - 文章对象
 */
function generateArticlePage(article) {
    const articleHtml = `<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="../favicon.ico" type="image/x-icon">
    <title>${article.title} - 谷比算力</title>
    <meta name="keywords" content="区块链策略开发, 量化交易策略, 数据采集, 行情数据接口, K线数据, 交易所API, 策略回测, Web3数据, 区块链数据分析, 自动化交易">
    <meta name="description" content="我们专注于区块链与量化交易领域，提供策略开发、数据采集、行情接口与回测服务，助力用户高效获取链上与交易所数据，打造智能化交易与分析解决方案。">    
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
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#4F46E5',
                        secondary: '#10B981',
                        dark: '#111827',
                        light: '#F9FAFB'
                    },
                    fontFamily: {
                        inter: ['Inter', 'system-ui', 'sans-serif'],
                    },
                }
            }
        }
    </script>
</head>
<body>
    <!-- 导航栏 -->
    <header class="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-md border-b border-gray-100 z-50 transition-all duration-300 shadow-sm">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16 sm:h-20">
                <!-- Logo - 点击跳转到首页 -->
                <a href="../index.html" class="flex items-center space-x-2 hover:opacity-90 transition-opacity duration-300">
                    <img src="../img/logo.png" alt="谷比算力 Logo" class="h-8 sm:h-10 w-auto">
                    <span href="../index.html" class="text-lg sm:text-xl font-bold text-primary" data-lang-key="site.name">谷比算力</span>
                </a>

                <!-- 操作按钮 -->
                <div class="flex items-center space-x-4">
                    <a href="https://t.me/mevjk_bot" target="_blank" class="hidden md:block px-4 py-2 rounded-full bg-primary text-white hover:bg-primary/90 font-medium transition-all-300 shadow-md hover:shadow-lg" data-lang-key="btn.start">
                        立即开始
                    </a>
                    <button class="md:hidden px-2 py-1 border border-primary/50 text-primary rounded-md hover:bg-primary/5 transition-colors" data-lang-switch>
                        <span data-lang-btn-text>EN</span>
                    </button>

                    <button class="hidden md:block px-4 py-2 rounded-full border border-primary text-primary hover:bg-primary/5 font-medium transition-all-300" data-lang-switch>
                        <span data-lang-btn-text>EN</span>
                    </button>
                </div>
            </div>
        </div>
    </header>

        <!-- 悬浮社交按钮 -->
    <div class="social-floating fixed bottom-24 right-6 z-50 flex flex-col gap-3">
        <a href="https://t.me/mevjk_bot" target="_blank" class="social-btn telegram w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <i class="fa fa-paper-plane text-xl"></i>
        </a>
        <a href="https://x.com/gubutdata" target="_blank" class="social-btn twitter w-12 h-12 rounded-full bg-gray-900 flex items-center justify-center text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <i class="fa fa-twitter text-xl"></i>
        </a>
    </div>

    <div class="article-container">
        <article class="article-content">
            <h1>${article.title}</h1>
            <div class="article-meta">
                <span data-lang="zh">发布于: </span><span data-lang="en" class="hidden-lang">Published: </span>${article.date}
            </div>
            <div class="article-body">
                ${article.content}
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
    
    <!-- 底部 -->
    <footer class="bg-gray-900 text-gray-400 py-10 border-t border-gray-800">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <div class="mb-6 md:mb-0">
                    <p class="text-sm" data-lang-key="footer.copyright">© 2024 谷比算力. 版权所有.</p>
                </div>
                <div class="flex space-x-6">
                    <a href="../privacy.html" class="text-gray-400 hover:text-white transition-colors" data-lang-key="footer.privacy">隐私政策</a>
                    <a href="../terms.html" class="text-gray-400 hover:text-white transition-colors" data-lang-key="footer.terms">使用条款</a>
                    <a href="#" class="text-gray-400 hover:text-white transition-colors" data-lang-key="footer.contact">联系我们</a>
                </div>
            </div>
            <div class="mt-8 pt-8 border-t border-gray-800 text-center text-sm" data-lang-key="footer.risk">
                风险提示：加密货币交易具有高风险，请谨慎投资
            </div>
        </div>
    </footer>
</body>
</html>`;

    // 将文章页面保存到new目录
    const fileName = path.join(newDir, `article-${article.id}.html`);
    fs.writeFileSync(fileName, articleHtml, 'utf8');
    console.log(`文章页面已生成: ${fileName}`);
}

/**
 * 更新网站地图
 * @param {Array} articles - 文章数组
 */
function updateSitemap(articles) {
    const sitemapPath = path.join(__dirname, 'sitemap.xml');
    let existingUrls = {};
    
    // 如果网站地图已存在，读取现有内容并解析
    if (fs.existsSync(sitemapPath)) {
        const sitemapData = fs.readFileSync(sitemapPath, 'utf8');
        // 提取现有的URL和它们的lastmod时间
        const urlRegex = /<url>[\s\S]*?<loc>(.*?)<\/loc>[\s\S]*?<lastmod>(.*?)<\/lastmod>[\s\S]*?<\/url>/g;
        let match;
        while ((match = urlRegex.exec(sitemapData)) !== null) {
            existingUrls[match[1]] = match[2]; // 保存URL和对应的lastmod
        }
    }
    
    let sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://www.gubut.com/index.html</loc>
        <lastmod>${existingUrls['https://www.gubut.com/index.html'] || new Date().toISOString().split('T')[0]}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>`;

    // 添加所有文章页面到网站地图
    articles.forEach(article => {
        const articleUrl = `https://www.gubut.com/new/article-${article.id}.html`;
        const lastModDate = existingUrls[articleUrl] || new Date().toISOString().split('T')[0];
        
        sitemapXml += `
    <url>
        <loc>${articleUrl}</loc>
        <lastmod>${lastModDate}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>`;
    });

    sitemapXml += `
</urlset>`;

    // 将网站地图保存到根目录
    fs.writeFileSync(sitemapPath, sitemapXml, 'utf8');
    console.log(`网站地图已更新: ${sitemapPath}`);
}

/**
 * 提取纯文本内容，移除HTML标签
 * @param {string} html - HTML内容
 * @returns {string} - 纯文本内容
 */
function extractTextFromHtml(html) {
    // 移除HTML标签，只保留纯文本
    let text = html.replace(/<[^>]*>/g, '');
    // 移除多余的空白字符
    text = text.replace(/\s+/g, ' ').trim();
    // 返回完整文本内容，不移除缩减限制
    return text;
}

/**
 * 更新文章JSON文件
 * @param {Object} newArticle - 新文章对象
 */
function updateArticlesJson(newArticle) {
    const articlesJsonPath = path.join(__dirname, 'articles.json');
    let articles = [];
    
    // 创建一个新的文章对象，只包含需要的信息
    const processedArticle = {
        id: newArticle.id,
        title: newArticle.title,
        date: newArticle.date,
        content: extractTextFromHtml(newArticle.content) // 处理内容，只保留前50个文字
    };
    
    // 如果articles.json文件存在，读取现有内容
    if (fs.existsSync(articlesJsonPath)) {
        const articlesData = fs.readFileSync(articlesJsonPath, 'utf8');
        articles = JSON.parse(articlesData);
    }
    
    // 检查文章是否已存在，如果存在则更新，否则添加
    const existingIndex = articles.findIndex(article => article.id === newArticle.id);
    if (existingIndex >= 0) {
        articles[existingIndex] = processedArticle;
    } else {
        articles.push(processedArticle);
    }
    
    // 保存更新后的文章列表
    fs.writeFileSync(articlesJsonPath, JSON.stringify(articles, null, 2), 'utf8');
    console.log(`文章JSON文件已更新: ${articlesJsonPath}`);
}

// 导出函数供其他模块使用
module.exports = {
    generateArticlePage,
    updateSitemap,
    updateArticlesJson
};