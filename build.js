// build.js - 用于生成文章页面和网站地图的构建脚本
// 运行方式: node build.js

const fs = require('fs');
const path = require('path');

// 确保new目录存在
const newDir = path.join(__dirname, 'new');
if (!fs.existsSync(newDir)) {
    fs.mkdirSync(newDir);
    console.log('已创建new目录');
}

console.log('开始生成文章页面和网站地图...');

try {
    // 从localStorage模拟获取文章数据
    // 在实际服务器环境中，这些数据应该来自数据库
    const articlesData = fs.readFileSync(path.join(__dirname, 'articles.json'), 'utf8');
    const articles = JSON.parse(articlesData);
    
    // 生成文章页面
    articles.forEach(article => {
        generateArticlePage(article);
    });
    
    // 更新网站地图
    updateSitemap(articles);
    
    console.log('所有文章页面和网站地图生成完成！');
} catch (error) {
    if (error.code === 'ENOENT') {
        console.log('未找到文章数据文件 (articles.json)，已创建示例文件');
        // 创建示例文章数据文件
        const sampleArticles = [
            {
                id: Date.now(),
                title: "示例文章",
                content: "<p>这是一篇示例文章的内容。</p><p>您可以在这里添加图片、链接等富文本内容。</p>",
                date: new Date().toLocaleString('zh-CN')
            }
        ];
        
        fs.writeFileSync(path.join(__dirname, 'articles.json'), JSON.stringify(sampleArticles, null, 2));
        console.log('已创建示例文章数据文件 articles.json');
    } else {
        console.error('处理过程中发生错误:', error);
    }
}

/**
 * 生成独立的文章HTML页面
 * @param {Object} article - 文章对象
 */
function generateArticlePage(article) {
    // 处理文章内容中的图片路径，确保它们是绝对路径
    let processedContent = article.content;
    
    // 使用正则表达式查找所有图片路径并转换为绝对路径
    // 匹配<img src="img/...">格式的标签
    processedContent = processedContent.replace(/<img\s+src="img\//g, '<img src="/img/');
    
    const articleHtml = `<!DOCTYPE html>
<html lang="en">
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
    <!-- 导航栏占位符 -->
    <div id="navbar-placeholder"></div>

    <div class="article-container">
        <article class="article-content">
            <h1>${article.title}</h1>
            <div class="article-meta">
                <span data-lang="zh">发布于: </span><span data-lang="en" class="hidden-lang">Published: </span>${article.date}
            </div>
            <div class="article-body">
                ${processedContent}
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
        // 页面加载完成后获取相关文章
        document.addEventListener('DOMContentLoaded', function() {
            loadRelatedArticles();
        });

        // 加载相关文章
        async function loadRelatedArticles() {
            const relatedArticlesList = document.getElementById('related-articles-list');

            try {
                // 从articles.json获取文章列表
                const response = await fetch('../articles.json');
                if (!response.ok) {
                    throw new Error('HTTP error! status: ' + response.status);
                }

                const articles = await response.json();
                
                // 获取当前文章ID（从URL中提取）
                const currentUrl = window.location.href;
                const matchResult = currentUrl.match(/article-(\\d+)\\.html/);
                const currentArticleId = matchResult ? matchResult[1] : null;

                // 过滤掉当前文章，并准备显示数据
                const relatedArticles = articles
                    .filter(article => article.id != currentArticleId) // 使用 != 因为ID可能是字符串或数字
                    .map(article => ({
                        id: article.id,
                        title: article.title,
                        date: article.date || "",  // 如果没有日期字段则为空
                        url: "../new/article-" + article.id + ".html"
                    }));

                // 按日期排序，最新的在前面
                relatedArticles.sort((a, b) => {
                    if (a.date && b.date) {
                        // 如果都有日期，按日期排序
                        return new Date(b.date) - new Date(a.date);
                    } else if (a.date) {
                        // 有日期的排在前面
                        return -1;
                    } else if (b.date) {
                        // 有日期的排在前面
                        return 1;
                    } else {
                        // 都没有日期，保持原有顺序
                        return 0;
                    }
                });

                displayRelatedArticles(relatedArticles);
            } catch (error) {
                console.error('加载相关文章失败:', error);
                relatedArticlesList.innerHTML = '<p>加载相关文章失败</p>';
            }
        }

        // 显示相关文章
        function displayRelatedArticles(articles) {
            const relatedArticlesList = document.getElementById('related-articles-list');

            if (!articles || articles.length === 0) {
                relatedArticlesList.innerHTML = '<p>暂无相关文章</p>';
                return;
            }

            // 最多显示20篇
            const relatedArticles = articles.slice(0, 20);

            // 清空当前列表
            relatedArticlesList.innerHTML = '';

            // 添加相关文章
            relatedArticles.forEach(article => {
                const relatedArticle = document.createElement('div');
                relatedArticle.className = 'related-article';

                // 构造文章显示内容
                let articleHTML = '<a href="' + article.url + '">' + escapeHtml(article.title) + '</a>';
                if (article.date) {
                    articleHTML += '<span class="related-article-date">' + article.date + '</span>';
                }

                relatedArticle.innerHTML = articleHTML;
                relatedArticlesList.appendChild(relatedArticle);
            });
        }

        // 简单的HTML转义函数，防止XSS攻击
        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };

            return text.replace(/[&<>"']/g, function(m) { return map[m]; });
        }
    </script>
</body>
</html>`;

    // 将文章页面保存到new目录
    const fileName = path.join(newDir, `article-${article.id}.html`);
    fs.writeFileSync(fileName, articleHtml, 'utf8');
    console.log(`✓ 已生成文章页面: ${path.basename(fileName)}`);
}

/**
 * 更新网站地图
 * @param {Array} articles - 文章数组
 */
function updateSitemap(articles) {
    // 使用generate-article.js中的通用网站地图生成函数
    const { updateSitemap: generateSitemap } = require('./generate-article');
    generateSitemap(articles);
}