const fs = require('fs');
const path = require('path');
const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');

// 导入generate-article模块中的函数
const { updateSitemap } = require('./generate-article');

const hostname = '127.0.0.1';
const PORT = process.env.PORT || 3000;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || '123456';

// 添加用于存储上传图片的目录
const imgDir = path.join(__dirname, 'img');

// 确保img目录存在
if (!fs.existsSync(imgDir)) {
    fs.mkdirSync(imgDir);
}

// 设置multer存储配置
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'img/')
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9)
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname))
  }
})

const upload = multer({ storage: storage })

// 创建Express应用
const app = express();

// 添加中间件
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 添加中间件来处理图片上传
app.post('/api/upload-image', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }
    
    // 返回图片访问路径（使用绝对路径格式，确保在任何目录下都能正确加载图片）
    res.json({
        location: `/img/${req.file.filename}`
    });
});

// 处理API请求
app.post('/api/generate-article', (req, res) => {
  generateArticleFile(req.body, res);
});

app.post('/api/save-article', (req, res) => {
  saveArticleData(req.body, res);
});

app.post('/api/update-article', (req, res) => {
  updateArticleData(req.body, res);
});

app.post('/api/delete-article', (req, res) => {
  deleteArticleData(req.body, res);
});

app.get('/api/articles', (req, res) => {
  getArticles(res);
});

app.get('/api/article/:id', (req, res) => {
  const articleId = parseInt(req.params.id);
  getArticleById(articleId, res);
});

// 获取所有文章
function getArticles(res) {
  const articlesPath = path.join(__dirname, 'articles.json');
  
  // 添加性能监控
  const startTime = Date.now();
  console.log(`[性能监控] 开始读取文章列表: ${startTime}`);
  
  fs.readFile(articlesPath, (err, data) => {
    const endTime = Date.now();
    console.log(`[性能监控] 文件读取完成，耗时: ${endTime - startTime}ms`);
    
    if (err) {
      if (err.code === 'ENOENT') {
        // 文件不存在，返回空数组
        console.log('[INFO] articles.json 文件不存在，返回空数组');
        res.set('Cache-Control', 'no-cache');
        res.json({ success: true, articles: [] });
      } else {
        console.error('[ERROR] 读取 articles.json 失败:', err);
        res.set('Cache-Control', 'no-cache');
        res.status(500).json({ success: false, message: 'Failed to read articles data' });
      }
    } else {
      try {
        const articles = JSON.parse(data);
        console.log(`[INFO] 成功加载 ${articles.length} 篇文章`);
        
        // 添加缓存控制头以提高性能
        res.set('Cache-Control', 'no-cache');
        res.json({ success: true, articles });
      } catch (parseErr) {
        console.error('[ERROR] 解析 articles.json 失败:', parseErr);
        res.set('Cache-Control', 'no-cache');
        res.status(500).json({ success: false, message: 'Failed to parse articles data' });
      }
    }
    
    const finishTime = Date.now();
    console.log(`[性能监控] 请求处理完成，总耗时: ${finishTime - startTime}ms`);
  });
}

// 根据ID获取单个文章
function getArticleById(articleId, res) {
  const articlesPath = path.join(__dirname, 'articles.json');
  
  // 添加性能监控
  const startTime = Date.now();
  console.log(`[性能监控] 开始读取文章 ID ${articleId}: ${startTime}`);
  
  fs.readFile(articlesPath, (err, data) => {
    const readTime = Date.now();
    console.log(`[性能监控] 文件读取完成，耗时: ${readTime - startTime}ms`);
    
    if (err) {
      if (err.code === 'ENOENT') {
        console.log(`[INFO] 文章 ID ${articleId} 未找到：articles.json 文件不存在`);
        res.set('Cache-Control', 'no-cache');
        res.status(404).json({ success: false, message: 'Article not found' });
      } else {
        console.error(`[ERROR] 读取 articles.json 失败:`, err);
        res.set('Cache-Control', 'no-cache');
        res.status(500).json({ success: false, message: 'Failed to read articles data' });
      }
    } else {
      try {
        const articles = JSON.parse(data);
        const article = articles.find(a => a.id == articleId); // 使用 == 以支持字符串和数字ID比较
        const parseTime = Date.now();
        console.log(`[性能监控] 文章解析完成，耗时: ${parseTime - readTime}ms`);
        
        if (article) {
          console.log(`[INFO] 成功找到文章 ID ${articleId}`);
          res.set('Cache-Control', 'no-cache');
          res.json({ success: true, article });
        } else {
          console.log(`[INFO] 文章 ID ${articleId} 未找到`);
          res.set('Cache-Control', 'no-cache');
          res.status(404).json({ success: false, message: 'Article not found' });
        }
      } catch (parseErr) {
        console.error('[ERROR] 解析 articles.json 失败:', parseErr);
        res.set('Cache-Control', 'no-cache');
        res.status(500).json({ success: false, message: 'Failed to parse articles data' });
      }
    }
    
    const finishTime = Date.now();
    console.log(`[性能监控] 请求处理完成，总耗时: ${finishTime - startTime}ms`);
  });
}

// 生成文章文件
function generateArticleFile(articleData, res) {
  const articleHtml = `<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${articleData.title} - 谷比算力</title>
    <!-- 引入样式文件 -->
    <link rel="stylesheet" href="../styles.css">
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar">
        <div class="navbar-brand">
            <img src="../img/logo.png" alt="谷比算力 Logo" class="navbar-logo">
            <h1 class="navbar-title">谷比算力</h1>
        </div>
        <button class="back-btn" onclick="location.href='../index.html'">返回首页</button>
    </nav>

    <div class="article-container">
        <article class="article-content">
            <h1>${articleData.title}</h1>
            <div class="article-meta">
                <span data-lang="zh">发布于: </span><span data-lang="en" class="hidden-lang">Published: </span>${articleData.date}
            </div>
            <div class="article-body">
                ${articleData.content}
            </div>
        </article>
    </div>

    <footer class="footer">
        <p>© 2024 谷比算力. 版权所有.</p>
    </footer>
</body>
</html>`;

  const fileName = path.join(__dirname, 'new', `article-${articleData.id}.html`);
  
  fs.writeFile(fileName, articleHtml, (err) => {
    if (err) {
      res.status(500).json({ success: false, message: 'Failed to generate article file' });
    } else {
      res.json({ success: true, message: 'Article file generated successfully', fileName });
    }
  });
}

// 保存文章数据到articles.json
function saveArticleData(articleData, res) {
  // 读取现有的文章数据
  const articlesPath = path.join(__dirname, 'articles.json');
  fs.readFile(articlesPath, (err, data) => {
    if (err && err.code !== 'ENOENT') {
      res.status(500).json({ success: false, message: 'Failed to read articles data' });
      return;
    }
    
    let articles = [];
    if (data) {
      try {
        articles = JSON.parse(data);
      } catch (parseErr) {
        // 如果解析失败，使用空数组
        articles = [];
      }
    }
    
    // 添加新文章到开头
    articles.unshift(articleData);
    
    // 写入文件
    fs.writeFile(articlesPath, JSON.stringify(articles, null, 2), (writeErr) => {
      if (writeErr) {
        res.status(500).json({ success: false, message: 'Failed to save article data' });
      } else {
        // 更新网站地图
        updateSitemapAfterChange(articles);
        
        // 保存成功后，执行build.js脚本重新生成文章页面
        const buildPath = path.join(__dirname, 'build.js');
        exec(`node "${buildPath}"`, (error, stdout, stderr) => {
          if (error) {
            console.error(`执行build.js时出错: ${error}`);
            res.json({ 
              success: true, 
              message: 'Article data saved successfully, but failed to build pages' 
            });
            return;
          }
          console.log(`build.js执行成功: ${stdout}`);
          res.json({ 
            success: true, 
            message: 'Article data saved and pages built successfully' 
          });
        });
      }
    });
  });
}

// 更新文章数据
function updateArticleData(articleData, res) {
  // 读取现有的文章数据
  const articlesPath = path.join(__dirname, 'articles.json');
  fs.readFile(articlesPath, (err, data) => {
    if (err && err.code !== 'ENOENT') {
      res.status(500).json({ success: false, message: 'Failed to read articles data' });
      return;
    }
    
    let articles = [];
    if (data) {
      try {
        articles = JSON.parse(data);
      } catch (parseErr) {
        articles = [];
      }
    }
    
    // 查找并更新文章
    const index = articles.findIndex(article => article.id === articleData.id);
    if (index !== -1) {
      articles[index] = articleData;
      
      // 写入文件
      fs.writeFile(articlesPath, JSON.stringify(articles, null, 2), (writeErr) => {
        if (writeErr) {
          res.status(500).json({ success: false, message: 'Failed to update article data' });
        } else {
          // 更新网站地图
          updateSitemapAfterChange(articles);
          
          // 更新成功后，执行build.js脚本重新生成文章页面
          const buildPath = path.join(__dirname, 'build.js');
          exec(`node "${buildPath}"`, (error, stdout, stderr) => {
            if (error) {
              console.error(`执行build.js时出错: ${error}`);
              res.json({ 
                success: true, 
                message: 'Article data updated successfully, but failed to build pages' 
              });
              return;
            }
            console.log(`build.js执行成功: ${stdout}`);
            res.json({ 
              success: true, 
              message: 'Article data updated and pages built successfully' 
            });
          });
        }
      });
    } else {
      res.status(404).json({ success: false, message: 'Article not found' });
    }
  });
}

// 删除文章数据
function deleteArticleData(articleData, res) {
  // 读取现有的文章数据
  const articlesPath = path.join(__dirname, 'articles.json');
  fs.readFile(articlesPath, (err, data) => {
    if (err && err.code !== 'ENOENT') {
      res.status(500).json({ success: false, message: 'Failed to read articles data' });
      return;
    }
    
    let articles = [];
    if (data) {
      try {
        articles = JSON.parse(data);
      } catch (parseErr) {
        articles = [];
      }
    }
    
    // 过滤掉要删除的文章
    const articleId = articleData.id;
    articles = articles.filter(article => article.id !== articleId);
    
    // 写入文件
    fs.writeFile(articlesPath, JSON.stringify(articles, null, 2), (writeErr) => {
      if (writeErr) {
        res.status(500).json({ success: false, message: 'Failed to delete article data' });
      } else {
        // 删除对应的HTML文件
        const htmlFilePath = path.join(__dirname, 'new', `article-${articleId}.html`);
        fs.unlink(htmlFilePath, (unlinkErr) => {
          if (unlinkErr && unlinkErr.code !== 'ENOENT') {
            console.error(`删除HTML文件失败: ${unlinkErr}`);
          } else if (!unlinkErr) {
            console.log(`✓ 已删除文章HTML文件: ${htmlFilePath}`);
          }
          
          // 更新网站地图
          updateSitemapAfterChange(articles);
          
          // 删除成功后，执行build.js脚本重新生成文章页面
          const buildPath = path.join(__dirname, 'build.js');
          exec(`node "${buildPath}"`, (error, stdout, stderr) => {
            if (error) {
              console.error(`执行build.js时出错: ${error}`);
              res.json({ 
                success: true, 
                message: 'Article data deleted successfully, but failed to build pages' 
              });
              return;
            }
            console.log(`build.js执行成功: ${stdout}`);
            
            res.json({ 
              success: true, 
              message: 'Article data deleted and pages rebuilt successfully' 
            });
          });
        });
      }
    });
  });
}

// 在文章变更后更新网站地图
function updateSitemapAfterChange(articles) {
    // 使用顶部导入的updateSitemap函数
    updateSitemap(articles);
}

// 获取网站配置
app.get('/api/site-config', (req, res) => {
    console.log('收到/api/site-config请求');
    const configPath = path.join(__dirname, 'site-config.json');
    
    fs.readFile(configPath, (err, data) => {
        if (err) {
            console.error('[ERROR] 读取site-config.json失败:', err);
            res.json({
                success: true,
                config: {
                    siteName: '谷比算力',
                    logo: 'img/logo.png',
                    keywords: '区块链, 算力, 量化交易, 策略开发, 加密货币',
                    description: '谷比算力 - 专注于区块链技术与量化交易策略的专业平台',
                    social: {
                        telegram: 'https://t.me/gubitrade',
                        twitter: 'https://twitter.com/gubitrade'
                    }
                }
            });
            return;
        }
        
        try {
            const config = JSON.parse(data);
            res.json({ success: true, config });
        } catch (parseErr) {
            console.error('[ERROR] 解析site-config.json失败:', parseErr);
            res.json({
                success: true,
                config: {
                    siteName: '谷比算力',
                    logo: 'img/logo.png',
                    keywords: '区块链, 算力, 量化交易, 策略开发, 加密货币',
                    description: '谷比算力 - 专注于区块链技术与量化交易策略的专业平台',
                    social: {
                        telegram: 'https://t.me/gubitrade',
                        twitter: 'https://twitter.com/gubitrade'
                    }
                }
            });
        }
    });
});

// 保存网站配置
app.post('/api/site-config', (req, res) => {
    const configPath = path.join(__dirname, 'site-config.json');
    const configData = req.body;
    
    fs.writeFile(configPath, JSON.stringify(configData, null, 2), (err) => {
        if (err) {
            console.error('[ERROR] 保存site-config.json失败:', err);
            res.status(500).json({ success: false, message: 'Failed to save site config' });
            return;
        }
        
        res.json({ success: true, message: 'Site config saved successfully' });
    });
});

// 更新文章
app.post('/api/update-article', (req, res) => {
    console.log('收到/api/update-article请求');
    const articleData = req.body;
    updateArticleData(articleData, res);
});

// 删除文章
app.post('/api/delete-article', (req, res) => {
    console.log('收到/api/delete-article请求');
    const articleData = req.body;
    deleteArticleData(articleData, res);
});

// 静态文件服务
app.use(express.static('.'));

// 所有其他请求返回404页面
app.use((req, res) => {
  console.log(`请求: ${req.url}`);
  
  // 特殊处理users.json文件
  if (req.url === '/users.json') {
    // 在生产环境中，可能需要添加身份验证来保护此文件
    // 这里我们允许访问，但在实际项目中应该添加适当的保护措施
    console.log('警告: users.json文件被访问');
  }
  
  // 尝试返回404页面
  fs.readFile('./404.html', (err, content404) => {
    if (err) {
      // 如果没有404页面，则发送简单错误信息
      res.status(404).send('<h1>404 Not Found</h1><p>The page you are looking for does not exist.</p>');
    } else {
      res.status(404).send(content404.toString());
    }
  });
});

app.listen(PORT, hostname, () => {
  console.log(`服务器运行在 http://${hostname}:${PORT}/`);
  console.log(`API端点:`);
  console.log(`  POST /api/generate-article`);
  console.log(`  POST /api/save-article`);
  console.log(`  POST /api/update-article`);
  console.log(`  POST /api/delete-article`);
  console.log(`  GET /api/articles`);
  console.log(`  GET /api/article/{id}`);
  console.log(`  POST /api/upload-image`);
  console.log(`  GET /api/site-config`);
  console.log(`  POST /api/site-config`);
});