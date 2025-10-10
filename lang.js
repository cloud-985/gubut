// 语言切换组件
class LanguageSwitcher {
    constructor() {
        // 存储所有需要翻译的文本
        this.translations = {
            zh: {
                'site.name': '谷比算力',
                'site.title': '谷比算力 - 专业区块链策略开发与量化交易服务',
                'site.keywords': '区块链策略开发, 量化交易策略, 数据采集, 行情数据接口, K线数据, 交易所API, 策略回测, Web3数据, 区块链数据分析, 自动化交易',
                'site.description': '我们专注于区块链与量化交易领域，提供策略开发、数据采集、行情接口与回测服务，助力用户高效获取链上与交易所数据，打造智能化交易与分析解决方案。',
                'nav.features': '核心优势',
                'nav.services': '服务内容',
                'nav.exchanges': '交易所分析',
                'nav.articles': '最新资讯',
                'btn.start': '立即开始',
                'btn.experience': '开始体验',
                'btn.demo': '观看演示',
                'btn.lang': 'EN',
                'hero.title': '专业区块链策略开发与量化交易服务',
                'hero.subtitle': '我们专注于区块链与量化交易领域，提供策略开发、数据采集、行情接口与回测服务，助力用户高效获取链上与交易所数据，打造智能化交易与分析解决方案。',
                'trusted.title': '受到行业领先企业的信任',
                'features.title': '我们的核心优势',
                'features.subtitle': '谷比算力凭借专业的技术团队和丰富的行业经验，为您提供全方位的区块链量化交易解决方案',
                'feature.smart.title': '智能交易系统',
                'feature.smart.desc': '利用先进的算法和机器学习技术，提供高效的智能交易解决方案，帮助用户最大化收益。我们的系统可以7x24小时不间断监控市场动态，自动执行交易策略。',
                'feature.risk.title': '风险控制系统',
                'feature.risk.desc': '通过多层次的风险控制体系，确保用户资产的安全性和稳定性。我们采用实时监控、动态止损和资产分散等多种手段，最大程度降低投资风险。',
                'feature.data.title': '数据分析服务',
                'feature.data.desc': '提供全面的区块链数据分析和可视化服务，帮助用户深入了解市场趋势和投资机会。我们的专业团队定期发布行业研究报告。',
                'services.title': '我们的服务内容',
                'services.subtitle': '提供全方位的区块链量化交易解决方案，助力您在数字资产领域取得成功',
                'services.chart.title': '服务效果数据',
                'service.strategy.title': '策略开发',
                'service.strategy.desc': '根据用户需求，开发个性化的交易策略，包括趋势跟踪、均值回归、网格交易等多种策略类型。我们的团队拥有丰富的策略开发经验，能够针对不同市场环境提供最佳解决方案。',
                'service.market.title': '行情分析',
                'service.market.desc': '提供实时行情数据和深度分析报告，帮助用户把握市场脉搏。我们的分析团队每日跟踪市场动态，提供专业的投资建议和风险提示。',
                'service.backtest.title': '策略回测',
                'service.backtest.desc': '利用历史数据对交易策略进行回测和优化，评估策略的盈利能力和风险水平。我们的回测系统支持多资产、多周期的测试，提供详细的回测报告和参数优化建议。',
                'service.api.title': '数据接口',
                'service.api.desc': '提供稳定、高效的行情数据和交易接口服务，支持多种主流交易所和数字资产。我们的数据接口具有低延迟、高可用性的特点，满足专业交易者的需求。',
                'exchanges.title': '交易所分析',
                'exchanges.subtitle': '通过我们的合作伙伴专属链接注册，可享受所有策略指标、交易工具和策略定制',
                'exchange.gate.title': '芝麻 (Gate.io)',
                'exchange.binance.title': '币安 (Binance)',
                'exchange.okx.title': '欧易 (OKX)',
                'articles.title': '最新资讯',
                'articles.subtitle': '了解区块链和量化交易的最新动态和深度分析',
                'articles.live': '实时更新',
                'articles.loading': '加载文章中...',
                'articles.more': '更多文章',
                'articles.viewAll': '查看所有文章 →',
                'signals.title': '交易信号服务',
                'signals.subtitle': '快人一步的行情数据，让你在别人还没反应时，就已经进场',
                'signal.new.title': '新币上线提醒',
                'signal.new.desc': '第一时间获取新币上线信息，抢占先机',
                'signal.market.title': '市场异动推送',
                'signal.market.desc': '实时推送资金流异常、盘口深度变化等关键信号',
                'signal.basic.title': '基础信号',
                'signal.basic.desc': '每日提供市场主要加密货币的基础交易信号',
                'signal.advanced.title': '高级信号',
                'signal.advanced.desc': '包含技术指标和市场情绪分析的高级交易信号',
                'signal.vip.title': 'VIP社群服务',
                'signal.vip.desc': '加入专属社群，获取全部信号和深度指标',
                'signal.btn': '免费获取信号',
                'footer.privacy': '隐私政策',
                'footer.terms': '使用条款',
                'footer.contact': '联系我们',
                'footer.risk': '风险提示：加密货币交易具有高风险，请谨慎投资',
                'footer.copyright': '© 2024 谷比算力. 版权所有.',
                'footer.tagline': '专业区块链策略开发与量化交易服务',
                'footer.quickLinks': '快捷链接',
                'footer.legal': '法律信息',
                'footer.disclaimer': '免责声明：本站内容仅供学习参考，不构成投资建议。加密货币交易存在高风险，请谨慎决策。',
                'nav.home': '首页',
                'articles.published': '发布于: ',
                'chat.btn': '在线客服',
                'exchange.founded': '成立时间',
                'exchange.pairs': '交易对数量',
                'exchange.headquarters': '总部',
                'exchange.volume': '24h交易量',
                'btn.register': '立即注册'
            },
            en: {
                'site.name': 'Gubi Analytics',
                'site.title': 'Gubi Analytics - Professional Blockchain Strategy Development & Quantitative Trading Services',
                '404.title': '404 - Page Not Found',
                '404.subtitle': 'Sorry, the page you are looking for does not exist.',
                '404.reasons': 'Possible reasons:',
                '404.reason.deleted': 'The page has been deleted or moved',
                '404.reason.url': 'Incorrect URL entered',
                '404.reason.notgenerated': 'The page has not been generated yet',
                '404.btn': 'Return to Homepage',
                'site.keywords': 'blockchain strategy development, quantitative trading strategy, data collection, market data interface, K-line data, exchange API, strategy backtesting, Web3 data, blockchain data analysis, automated trading',
                'site.description': 'We specialize in blockchain and quantitative trading, providing strategy development, data collection, market interfaces, and backtesting services to help users efficiently obtain on-chain and exchange data, creating intelligent trading and analysis solutions.',
                'nav.features': 'Core Advantages',
                'nav.services': 'Services',
                'nav.exchanges': 'Exchange Analysis',
                'nav.articles': 'Latest News',
                'btn.start': 'Get Started',
                'btn.experience': 'Start Experience',
                'btn.demo': 'Watch Demo',
                'btn.lang': '中文',
                'hero.title': 'Professional Blockchain Strategy Development & Quantitative Trading Services',
                'hero.subtitle': 'We specialize in blockchain and quantitative trading, providing strategy development, data collection, market interfaces, and backtesting services to help users efficiently obtain on-chain and exchange data, creating intelligent trading and analysis solutions.',
                'trusted.title': 'Trusted by industry-leading companies',
                'features.title': 'Our Core Advantages',
                'features.subtitle': 'With a professional technical team and rich industry experience, Gubi Analytics provides you with comprehensive blockchain quantitative trading solutions',
                'feature.smart.title': 'Intelligent Trading System',
                'feature.smart.desc': 'Using advanced algorithms and machine learning technology, we provide efficient intelligent trading solutions to help users maximize returns. Our system can monitor market dynamics 24/7 and automatically execute trading strategies.',
                'feature.risk.title': 'Risk Control System',
                'feature.risk.desc': 'Through a multi-level risk control system, we ensure the security and stability of user assets. We adopt various methods such as real-time monitoring, dynamic stop-loss, and asset diversification to minimize investment risks.',
                'feature.data.title': 'Data Analysis Services',
                'feature.data.desc': 'Provide comprehensive blockchain data analysis and visualization services to help users gain in-depth understanding of market trends and investment opportunities. Our professional team regularly publishes industry research reports.',
                'services.title': 'Our Services',
                'services.subtitle': 'Providing comprehensive blockchain quantitative trading solutions to help you succeed in the digital asset field',
                'services.chart.title': 'Service Performance Data',
                'service.strategy.title': 'Strategy Development',
                'service.strategy.desc': 'Develop personalized trading strategies according to user needs, including trend tracking, mean reversion, grid trading and other strategy types. Our team has rich experience in strategy development and can provide the best solutions for different market environments.',
                'service.market.title': 'Market Analysis',
                'service.market.desc': 'Provide real-time market data and in-depth analysis reports to help users grasp market trends. Our analysis team tracks market dynamics daily and provides professional investment advice and risk warnings.',
                'service.backtest.title': 'Strategy Backtesting',
                'service.backtest.desc': 'Backtest and optimize trading strategies using historical data to evaluate the profitability and risk level of strategies. Our backtesting system supports multi-asset, multi-period testing and provides detailed backtesting reports and parameter optimization recommendations.',
                'service.api.title': 'Data Interface',
                'service.api.desc': 'Provide stable, efficient market data and trading interface services that support multiple mainstream exchanges and digital assets. Our data interface has the characteristics of low latency and high availability to meet the needs of professional traders.',
                'exchanges.title': 'Exchange Analysis',
                'exchanges.subtitle': 'Register through our partners exclusive link to enjoy all strategy indicators, trading tools, and strategy customization.',
                'exchange.gate.title': 'Gate.io',
                'exchange.binance.title': 'Binance',
                'exchange.okx.title': 'OKX',
                
                // 交易所基本信息标签
                'exchange.info.founded': 'Founded',
                'exchange.info.pairs': 'Trading Pairs',
                'exchange.info.headquarters': 'Headquarters',
                'exchange.info.volume': '24h Volume',
                'exchange.info.fee': 'Trading Fee',
                'exchange.info.currencies': 'Supported Currencies',
                'exchange.info.rating': 'Rating',
                
                // 交易所优缺点标题
                'exchange.pros.title': 'Advantages',
                'exchange.cons.title': 'Disadvantages',
                
                // Gate.io 优缺点
                'exchange.gate.pros.1': 'Rich trading pairs, including many mainstream and niche cryptocurrencies',
                'exchange.gate.pros.2': 'Simple and user-friendly interface, suitable for beginners',
                'exchange.gate.pros.3': 'Low trading fees with VIP rate system',
                'exchange.gate.cons.1': 'Slow customer support response, long problem resolution time',
                'exchange.gate.cons.2': 'Limited support in some countries and regions',
                
                // Binance 优缺点
                'exchange.binance.pros.1': 'Largest cryptocurrency exchange globally with high liquidity',
                'exchange.binance.pros.2': 'Over 1000 trading currencies, extremely rich selection',
                'exchange.binance.pros.3': 'Stable trading platform with excellent user experience',
                'exchange.binance.pros.4': 'Provides Binance Smart Chain (BSC) with complete ecosystem',
                'exchange.binance.cons.1': 'Restrictive policies for users in certain countries and regions',
                'exchange.binance.cons.2': 'Faces regulatory scrutiny and policy risks',
                
                // OKX 优缺点
                'exchange.okx.pros.1': 'Rich trading functions including spot, futures, options and other trading types',
                'exchange.okx.pros.2': 'Mature futures trading system, leading global trading volume',
                'exchange.okx.pros.3': 'High security level with no major security incidents in history',
                'exchange.okx.pros.4': 'Provides OKC public chain and rich DeFi ecosystem support',
                'exchange.okx.cons.1': 'Relatively complex interface design, requiring adaptation time for beginners',
                'exchange.okx.cons.2': 'Some advanced functions are not friendly enough for beginners',
                
                // XT 优缺点
                'exchange.xt.pros.1': 'Rich platform activities, regularly launching various trading competitions and reward events',
                'exchange.xt.pros.2': 'Stable and smooth trading system, rarely experiencing lag or delay',
                'exchange.xt.pros.3': 'Overall good user experience with timely customer service response',
                'exchange.xt.cons.1': 'Relatively fewer supported currencies, especially niche ones',
                'exchange.xt.cons.2': 'Average market depth, possible slippage issues for large transactions',
                
                // Bitget 优缺点
                'exchange.bitget.pros.1': 'Powerful futures trading system supporting multiple contract types and leverage multiples',
                'exchange.bitget.pros.2': 'Innovative copy trading function, suitable for beginners following professional traders',
                'exchange.bitget.pros.3': 'Clean and clear interface design with convenient operation',
                'exchange.bitget.cons.1': 'Relatively weak spot trading function with smaller trading volume',
                'exchange.bitget.cons.2': 'Insufficient market depth for some trading pairs, affecting trading experience',
                
                // Bitunix 优缺点
                'exchange.bitunix.pros.1': 'Clean and friendly UI design with smooth operation',
                'exchange.bitunix.pros.2': 'Fast new coin listing speed, often with hot project premieres',
                'exchange.bitunix.pros.3': 'Rich platform activities with较多 rewards and benefits',
                'exchange.bitunix.cons.1': 'Relatively small overall trading volume with insufficient liquidity for some currencies',
                'exchange.bitunix.cons.2': 'Relatively low visibility in the cryptocurrency market',
                'articles.title': 'Latest News',
                'articles.subtitle': 'Stay updated with the latest blockchain and quantitative trading insights',
                'articles.live': 'Real-time Updates',
                'articles.loading': 'Loading articles...',
                'articles.more': 'More Articles',
                'articles.viewAll': 'View All Articles →',
                'signals.title': 'Trading Signal Services',
                'signals.subtitle': 'Get ahead of the market with real-time data signals',
                'signal.new.title': 'New Coin Alerts',
                'signal.new.desc': 'Get first-hand information on new coin listings',
                'signal.market.title': 'Market Movement Alerts',
                'signal.market.desc': 'Real-time alerts for unusual fund flows and order book changes',
                'signal.basic.title': 'Basic Signals',
                'signal.basic.desc': 'Daily basic trading signals for major cryptocurrencies',
                'signal.advanced.title': 'Advanced Signals',
                'signal.advanced.desc': 'Advanced signals with technical indicators and market sentiment',
                'signal.vip.title': 'VIP Community Service',
                'signal.vip.desc': 'Join our exclusive community for full signals and deep indicators',
                'signal.btn': 'Get Free Signals',
                'footer.privacy': 'Privacy Policy',
                'footer.terms': 'Terms of Service',
                'footer.contact': 'Contact Us',
                'footer.risk': 'Risk Warning: Cryptocurrency trading involves high risk, invest cautiously',
                'footer.copyright': '© 2024 Gubi Analytics. All rights reserved.',
                'footer.tagline': 'Professional Blockchain Strategy Development & Quantitative Trading Services',
                'footer.quickLinks': 'Quick Links',
                'footer.legal': 'Legal Information',
                'footer.disclaimer': 'Disclaimer: The content on this site is for educational purposes only and does not constitute investment advice. Cryptocurrency trading involves high risk, please make decisions cautiously.',
                'nav.home': 'Home',
                'articles.published': 'Published: ',
                'chat.btn': 'Online Support',
                'exchange.founded': 'Founded',
                'exchange.pairs': 'Trading Pairs',
                'exchange.headquarters': 'Headquarters',
                'exchange.volume': '24h Volume',
                'btn.register': 'Register Now'
            }
        };
        
        // 当前语言
        this.currentLang = 'zh';
    }
    
    // 初始化语言组件
    init() {
        console.log('LanguageSwitcher: Initializing...');
        // 从localStorage中读取保存的语言设置
        const savedLang = localStorage.getItem('preferredLanguage');
        console.log('LanguageSwitcher: Saved language from localStorage:', savedLang);
        if (savedLang && (savedLang === 'zh' || savedLang === 'en')) {
            this.currentLang = savedLang;
        }
        
        console.log('LanguageSwitcher: Current language set to:', this.currentLang);
        
        // 设置默认语言
        document.documentElement.lang = this.currentLang;
        
        // 初始化语言切换按钮
        this.initLangSwitchBtn();
        
        // 翻译页面内容
        this.translatePage();
        
        // 监听DOM变化，动态翻译新添加的内容
        this.observeDOMChanges();
        
        console.log('LanguageSwitcher: Initialization complete');
    }
    
    // 初始化语言切换按钮
    initLangSwitchBtn() {
        const langBtns = document.querySelectorAll('[data-lang-switch]');
        langBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.toggleLanguage();
            });
            
            // 更新按钮文本
            const langText = btn.querySelector('[data-lang-btn-text]');
            if (langText) {
                langText.textContent = this.translations[this.currentLang]['btn.lang'];
            }
        });
    }
    
    // 切换语言
    toggleLanguage() {
        console.log('LanguageSwitcher: Toggling language from', this.currentLang);
        this.currentLang = this.currentLang === 'zh' ? 'en' : 'zh';
        document.documentElement.lang = this.currentLang;
        
        // 保存语言设置到localStorage
        localStorage.setItem('preferredLanguage', this.currentLang);
        
        // 翻译页面内容
        this.translatePage();
        
        // 更新语言切换按钮文本
        const langBtns = document.querySelectorAll('[data-lang-switch]');
        langBtns.forEach(btn => {
            const langText = btn.querySelector('[data-lang-btn-text]');
            if (langText) {
                langText.textContent = this.translations[this.currentLang]['btn.lang'];
            }
        });
        
        // 强制重新应用样式，确保所有元素都正确显示或隐藏
        this.forceReapplyStyles();
        
        // 触发语言切换事件，供其他组件监听
        const langChangeEvent = new CustomEvent('languageChanged', {
            detail: { language: this.currentLang }
        });
        document.dispatchEvent(langChangeEvent);
        
        console.log('LanguageSwitcher: Language toggled to', this.currentLang);
    }
    
    // 强制重新应用样式
    forceReapplyStyles() {
        console.log('LanguageSwitcher: Forcing reapplication of styles');
        
        // 重新检查并设置所有data-lang属性的元素
        const allLangElements = document.querySelectorAll('[data-lang]');
        allLangElements.forEach(element => {
            const elementLang = element.getAttribute('data-lang');
            if (elementLang === this.currentLang) {
                // 确保显示当前语言的元素
                element.style.display = '';
                element.style.display = 'block'; // 显式设置为block
                // 移除hidden-lang类
                if (element.classList.contains('hidden-lang')) {
                    element.classList.remove('hidden-lang');
                    console.log('LanguageSwitcher: Removed hidden-lang class during force reapply');
                }
            } else {
                // 确保隐藏其他语言的元素
                element.style.display = 'none';
                // 添加hidden-lang类
                if (!element.classList.contains('hidden-lang')) {
                    element.classList.add('hidden-lang');
                    console.log('LanguageSwitcher: Added hidden-lang class during force reapply');
                }
            }
        });
        
        console.log('LanguageSwitcher: Force reapplication of styles complete');
    }
    
    // 翻译页面内容
    translatePage() {
        console.log('LanguageSwitcher: Translating page to', this.currentLang);
        
        // 使用data-lang-key属性的元素
        const elements = document.querySelectorAll('[data-lang-key]');
        console.log('LanguageSwitcher: Found', elements.length, 'elements with data-lang-key');
        elements.forEach(element => {
            const key = element.getAttribute('data-lang-key');
            if (this.translations[this.currentLang][key]) {
                element.textContent = this.translations[this.currentLang][key];
            }
        });
        
        // 使用data-lang属性的现有元素（兼容旧的实现）
        const legacyElements = document.querySelectorAll('[data-lang]');
        console.log('LanguageSwitcher: Found', legacyElements.length, 'elements with data-lang');
        
        let visibleElements = 0;
        let hiddenElements = 0;
        
        legacyElements.forEach(element => {
            const elementLang = element.getAttribute('data-lang');
            if (elementLang === this.currentLang) {
                // 确保显示当前语言的元素
                element.style.display = '';
                element.style.display = 'block'; // 显式设置为block，确保覆盖其他样式
                // 移除hidden-lang类
                if (element.classList.contains('hidden-lang')) {
                    element.classList.remove('hidden-lang');
                    console.log('LanguageSwitcher: Removed hidden-lang class from element with lang', elementLang);
                }
                visibleElements++;
            } else {
                // 确保隐藏其他语言的元素
                element.style.display = 'none';
                // 添加hidden-lang类以确保隐藏
                if (!element.classList.contains('hidden-lang')) {
                    element.classList.add('hidden-lang');
                    console.log('LanguageSwitcher: Added hidden-lang class to element with lang', elementLang);
                }
                hiddenElements++;
            }
        });
        
        console.log('LanguageSwitcher: Visible elements count:', visibleElements);
        console.log('LanguageSwitcher: Hidden elements count:', hiddenElements);
        
        // 更新页面标题和meta标签
        document.title = this.translations[this.currentLang]['site.title'];
        console.log('LanguageSwitcher: Updated page title to', document.title);
        
        const keywordsMeta = document.querySelector('meta[name="keywords"]');
        if (keywordsMeta) {
            keywordsMeta.setAttribute('content', this.translations[this.currentLang]['site.keywords']);
        }
        
        const descMeta = document.querySelector('meta[name="description"]');
        if (descMeta) {
            descMeta.setAttribute('content', this.translations[this.currentLang]['site.description']);
        }
        
        console.log('LanguageSwitcher: Translation complete');
    }
    
    // 监听DOM变化，动态翻译新添加的内容
    observeDOMChanges() {
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // 元素节点
                        // 翻译新添加的元素
                        const newElements = node.querySelectorAll('[data-lang-key]');
                        newElements.forEach(element => {
                            const key = element.getAttribute('data-lang-key');
                            if (this.translations[this.currentLang][key]) {
                                element.textContent = this.translations[this.currentLang][key];
                            }
                        });
                        
                        // 处理带有data-lang属性的新元素
                        const newLegacyElements = node.querySelectorAll('[data-lang]');
                        newLegacyElements.forEach(element => {
                            if (element.getAttribute('data-lang') === this.currentLang) {
                                element.style.display = '';
                            } else {
                                element.style.display = 'none';
                            }
                        });
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // 获取当前语言
    getCurrentLanguage() {
        return this.currentLang;
    }
    
    // 获取翻译文本
    translate(key) {
        return this.translations[this.currentLang][key] || key;
    }
    
    // 添加新的翻译文本
    addTranslations(lang, translations) {
        if (!this.translations[lang]) {
            this.translations[lang] = {};
        }
        Object.assign(this.translations[lang], translations);
    }
}

// 创建全局实例
const langSwitcher = new LanguageSwitcher();

// DOM加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => langSwitcher.init());
} else {
    langSwitcher.init();
}