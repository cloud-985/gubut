const fs = require('fs');
const path = require('path');
const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const mysql = require('mysql2');
const bcrypt = require('bcrypt');

// 导入generate-article模块中的函数
const { updateSitemap } = require('./generate-article');

const hostname = '127.0.0.1';
const PORT = process.env.PORT || 3000;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || '123456';
const SALT_ROUNDS = 10;

// 创建MySQL连接池
const db = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'gubut',
  password: process.env.DB_PASSWORD || 'cG5wFz4isdSxaYc4',
  database: process.env.DB_NAME || 'gubut',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

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

// 数据库初始化
function initializeDatabase() {
  const createUsersTable = `
    CREATE TABLE IF NOT EXISTS users (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(50) UNIQUE NOT NULL,
      email VARCHAR(100) UNIQUE NOT NULL,
      password VARCHAR(255) NOT NULL,
      has_strategy_access BOOLEAN DEFAULT FALSE,
      strategy_expiry DATETIME NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
  `;
  
  const createStrategiesTable = `
    CREATE TABLE IF NOT EXISTS strategies (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      description TEXT,
      external_url VARCHAR(255),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
  `;
  
  // Check if columns exist and add them if they don't
  const checkColumnsQuery = `
    SELECT COUNT(*) AS count 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'users' AND COLUMN_NAME IN ('has_strategy_access', 'strategy_expiry')
  `;
  
  db.query(createUsersTable, (err) => {
    if (err) {
      console.error('创建用户表失败:', err);
      console.error('错误代码:', err.code);
      console.error('错误信息:', err.message);
    } else {
      console.log('用户表已创建或已存在');
    }
  });
  
  // Add strategy columns to existing table
  db.query(checkColumnsQuery, (err, results) => {
    if (err) {
      console.error('检查列存在性失败:', err);
      return;
    }
    
    const columnCount = results[0].count;
    
    // If columns don't exist, add them
    if (columnCount < 2) {
      const addColumnsQueries = [
        "ALTER TABLE users ADD COLUMN has_strategy_access BOOLEAN DEFAULT FALSE",
        "ALTER TABLE users ADD COLUMN strategy_expiry DATETIME NULL"
      ];
      
      addColumnsQueries.forEach(query => {
        db.query(query, (err) => {
          if (err) {
            // Ignore if column already exists
            if (err.code !== 'ER_DUP_FIELDNAME') {
              console.error('添加列失败:', err);
            }
          } else {
            console.log('成功添加列:', query);
          }
        });
      });
    } else {
      console.log('策略相关列已存在');
    }
  });
  
  db.query(createStrategiesTable, (err) => {
    if (err) {
      console.error('创建策略表失败:', err);
      console.error('错误代码:', err.code);
      console.error('错误信息:', err.message);
    } else {
      console.log('策略表已创建或已存在');
    }
  });
}

// 先定义所有API路由
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

// 用户管理API
// 获取所有用户
app.get('/api/users', (req, res) => {
  const query = 'SELECT id, username, email, created_at, has_strategy_access, strategy_expiry FROM users ORDER BY created_at DESC';
  
  db.query(query, (err, results) => {
    if (err) {
      console.error('查询用户失败:', err);
      return res.status(500).json({ success: false, message: '获取用户列表失败' });
    }
    
    res.json({ success: true, users: results });
  });
});

// 获取单个用户
app.get('/api/users/:id', (req, res) => {
  const userId = req.params.id;
  const query = 'SELECT id, username, email, created_at, has_strategy_access, strategy_expiry FROM users WHERE id = ?';
  
  db.query(query, [userId], (err, results) => {
    if (err) {
      console.error('查询用户失败:', err);
      return res.status(500).json({ success: false, message: '获取用户信息失败' });
    }
    
    if (results.length === 0) {
      return res.status(404).json({ success: false, message: '用户未找到' });
    }
    
    res.json({ success: true, user: results[0] });
  });
});

// 用户注册
app.post('/api/register', (req, res) => {
  const { username, email, password } = req.body;
  
  if (!username || !email || !password) {
    return res.status(400).json({ success: false, message: '用户名、邮箱和密码都是必填项' });
  }
  
  // 简单的密码强度检查
  if (password.length < 6) {
    return res.status(400).json({ success: false, message: '密码长度至少为6位' });
  }
  
  // 对密码进行哈希处理
  bcrypt.hash(password, SALT_ROUNDS, (err, hashedPassword) => {
    if (err) {
      console.error('密码哈希处理失败:', err);
      return res.status(500).json({ success: false, message: '注册失败' });
    }
    
    const query = 'INSERT INTO users (username, email, password, has_strategy_access, strategy_expiry) VALUES (?, ?, ?, ?, ?)';
    const values = [username, email, hashedPassword, false, null];
    
    db.query(query, values, (err, result) => {
      if (err) {
        console.error('创建用户失败:', err);
        if (err.code === 'ER_DUP_ENTRY') {
          return res.status(400).json({ success: false, message: '用户名或邮箱已存在' });
        }
        return res.status(500).json({ success: false, message: '创建用户失败' });
      }
      
      // 返回用户信息（不包含密码）
      const user = { 
        id: result.insertId, 
        username, 
        email, 
        created_at: new Date(),
        has_strategy_access: false,
        strategy_expiry: null
      };
      res.json({ success: true, message: '用户注册成功', user });
    });
  });
});

// 用户登录
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  
  if (!username || !password) {
    return res.status(400).json({ success: false, message: '用户名和密码都是必填项' });
  }
  
  const query = 'SELECT id, username, email, password, created_at, has_strategy_access, strategy_expiry FROM users WHERE username = ?';
  
  db.query(query, [username], (err, results) => {
    if (err) {
      console.error('查询用户失败:', err);
      return res.status(500).json({ success: false, message: '登录失败' });
    }
    
    if (results.length === 0) {
      return res.status(401).json({ success: false, message: '用户名或密码错误' });
    }
    
    const user = results[0];
    
    // Check if user has strategy access and if it's still valid
    if (user.has_strategy_access) {
      if (user.strategy_expiry && new Date() > new Date(user.strategy_expiry)) {
        // Access expired
        user.has_strategy_access = false;
      }
    }
    
    // 验证密码
    bcrypt.compare(password, user.password, (err, isMatch) => {
      if (err) {
        console.error('密码验证失败:', err);
        return res.status(500).json({ success: false, message: '登录失败' });
      }
      
      if (!isMatch) {
        return res.status(401).json({ success: false, message: '用户名或密码错误' });
      }
      
      // 移除密码字段
      delete user.password;
      
      // 在实际应用中，这里应该生成一个JWT token
      const token = 'fake-jwt-token-for-demo'; // 仅为演示，实际应使用JWT
      
      res.json({ success: true, message: '登录成功', user, token });
    });
  });
});

// 创建新用户（管理员接口）
app.post('/api/users', (req, res) => {
  const { username, email, password } = req.body;
  
  if (!username || !email || !password) {
    return res.status(400).json({ success: false, message: '用户名、邮箱和密码都是必填项' });
  }
  
  // 对密码进行哈希处理
  bcrypt.hash(password, SALT_ROUNDS, (err, hashedPassword) => {
    if (err) {
      console.error('密码哈希处理失败:', err);
      return res.status(500).json({ success: false, message: '创建用户失败' });
    }
    
    const query = 'INSERT INTO users (username, email, password) VALUES (?, ?, ?)';
    const values = [username, email, hashedPassword];
    
    db.query(query, values, (err, result) => {
      if (err) {
        console.error('创建用户失败:', err);
        if (err.code === 'ER_DUP_ENTRY') {
          return res.status(400).json({ success: false, message: '用户名或邮箱已存在' });
        }
        return res.status(500).json({ success: false, message: '创建用户失败' });
      }
      
      res.json({ success: true, message: '用户创建成功', userId: result.insertId });
    });
  });
});

// 更新用户信息
app.put('/api/users/:id', (req, res) => {
  const userId = req.params.id;
  const { username, email, password } = req.body;
  
  if (!username || !email) {
    return res.status(400).json({ success: false, message: '用户名和邮箱都是必填项' });
  }
  
  // 如果提供了密码，则对其进行哈希处理
  if (password) {
    bcrypt.hash(password, SALT_ROUNDS, (err, hashedPassword) => {
      if (err) {
        console.error('密码哈希处理失败:', err);
        return res.status(500).json({ success: false, message: '更新用户失败' });
      }
      
      const query = 'UPDATE users SET username = ?, email = ?, password = ? WHERE id = ?';
      const values = [username, email, hashedPassword, userId];
      
      db.query(query, values, (err, result) => {
        if (err) {
          console.error('更新用户失败:', err);
          if (err.code === 'ER_DUP_ENTRY') {
            return res.status(400).json({ success: false, message: '用户名或邮箱已存在' });
          }
          return res.status(500).json({ success: false, message: '更新用户失败' });
        }
        
        if (result.affectedRows === 0) {
          return res.status(404).json({ success: false, message: '用户未找到' });
        }
        
        res.json({ success: true, message: '用户更新成功' });
      });
    });
  } else {
    // 如果没有提供密码，则只更新用户名和邮箱
    const query = 'UPDATE users SET username = ?, email = ? WHERE id = ?';
    const values = [username, email, userId];
    
    db.query(query, values, (err, result) => {
      if (err) {
        console.error('更新用户失败:', err);
        if (err.code === 'ER_DUP_ENTRY') {
          return res.status(400).json({ success: false, message: '用户名或邮箱已存在' });
        }
        return res.status(500).json({ success: false, message: '更新用户失败' });
      }
      
      if (result.affectedRows === 0) {
        return res.status(404).json({ success: false, message: '用户未找到' });
      }
      
      res.json({ success: true, message: '用户更新成功' });
    });
  }
});

// 更新用户策略权限
app.put('/api/users/:id/strategy', (req, res) => {
  const userId = req.params.id;
  const { has_strategy_access, strategy_expiry } = req.body;
  
  const query = 'UPDATE users SET has_strategy_access = ?, strategy_expiry = ? WHERE id = ?';
  const values = [has_strategy_access, strategy_expiry || null, userId];
  
  db.query(query, values, (err, result) => {
    if (err) {
      console.error('更新用户策略权限失败:', err);
      return res.status(500).json({ success: false, message: '更新用户策略权限失败' });
    }
    
    if (result.affectedRows === 0) {
      return res.status(404).json({ success: false, message: '用户未找到' });
    }
    
    res.json({ success: true, message: '用户策略权限更新成功' });
  });
});

// 删除用户
app.delete('/api/users/:id', (req, res) => {
  const userId = req.params.id;
  const query = 'DELETE FROM users WHERE id = ?';
  
  db.query(query, [userId], (err, result) => {
    if (err) {
      console.error('删除用户失败:', err);
      return res.status(500).json({ success: false, message: '删除用户失败' });
    }
    
    if (result.affectedRows === 0) {
      return res.status(404).json({ success: false, message: '用户未找到' });
    }
    
    res.json({ success: true, message: '用户删除成功' });
  });
});

// 策略管理API
// 获取所有策略
app.get('/api/strategies', (req, res) => {
  const query = 'SELECT * FROM strategies ORDER BY created_at DESC';
  
  db.query(query, (err, results) => {
    if (err) {
      console.error('查询策略失败:', err);
      console.error('错误代码:', err.code);
      console.error('错误信息:', err.message);
      return res.status(500).json({ success: false, message: '获取策略列表失败: ' + err.message });
    }
    
    res.json({ success: true, strategies: results });
  });
});

// 获取单个策略
app.get('/api/strategies/:id', (req, res) => {
  const strategyId = req.params.id;
  const query = 'SELECT * FROM strategies WHERE id = ?';
  
  db.query(query, [strategyId], (err, results) => {
    if (err) {
      console.error('查询策略失败:', err);
      console.error('错误代码:', err.code);
      console.error('错误信息:', err.message);
      return res.status(500).json({ success: false, message: '获取策略失败: ' + err.message });
    }
    
    if (results.length === 0) {
      return res.status(404).json({ success: false, message: '策略未找到' });
    }
    
    res.json({ success: true, strategy: results[0] });
  });
});

// 创建新策略
app.post('/api/strategies', (req, res) => {
  const { name, description, external_url } = req.body;
  
  if (!name) {
    return res.status(400).json({ success: false, message: '策略名称是必填项' });
  }
  
  const query = 'INSERT INTO strategies (name, description, external_url) VALUES (?, ?, ?)';
  const values = [name, description, external_url];
  
  db.query(query, values, (err, result) => {
    if (err) {
      console.error('创建策略失败:', err);
      console.error('错误代码:', err.code);
      console.error('错误信息:', err.message);
      return res.status(500).json({ success: false, message: '创建策略失败: ' + err.message });
    }
    
    // 策略创建成功后更新网站地图
    updateSitemapAfterStrategyChange();
    
    res.json({ success: true, message: '策略创建成功', strategyId: result.insertId });
  });
});

// 更新策略信息
app.put('/api/strategies/:id', (req, res) => {
  const strategyId = req.params.id;
  const { name, description, external_url } = req.body;
  
  if (!name) {
    return res.status(400).json({ success: false, message: '策略名称是必填项' });
  }
  
  const query = 'UPDATE strategies SET name = ?, description = ?, external_url = ? WHERE id = ?';
  const values = [name, description, external_url, strategyId];
  
  db.query(query, values, (err, result) => {
    if (err) {
      console.error('更新策略失败:', err);
      console.error('错误代码:', err.code);
      console.error('错误信息:', err.message);
      return res.status(500).json({ success: false, message: '更新策略失败: ' + err.message });
    }
    
    if (result.affectedRows === 0) {
      return res.status(404).json({ success: false, message: '策略未找到' });
    }
    
    // 策略更新成功后更新网站地图
    updateSitemapAfterStrategyChange();
    
    res.json({ success: true, message: '策略更新成功' });
  });
});

// 删除策略
app.delete('/api/strategies/:id', (req, res) => {
  const strategyId = req.params.id;
  const query = 'DELETE FROM strategies WHERE id = ?';
  
  db.query(query, [strategyId], (err, result) => {
    if (err) {
      console.error('删除策略失败:', err);
      console.error('错误代码:', err.code);
      console.error('错误信息:', err.message);
      return res.status(500).json({ success: false, message: '删除策略失败: ' + err.message });
    }
    
    if (result.affectedRows === 0) {
      return res.status(404).json({ success: false, message: '策略未找到' });
    }
    
    // 策略删除成功后更新网站地图
    updateSitemapAfterStrategyChange();
    
    res.json({ success: true, message: '策略删除成功' });
  });
});

// 文章管理API
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
                        twitter: 'https://twitter.com/gubitrade',
                        discord: 'discord_link'
                    },
                    exchanges: {
                        gate: 'https://www.gatenode.cloud/signup/VLURVV9EVG?ref_type=103',
                        binance: 'https://accounts.maxweb.black/register?ref=1090079770',
                        okx: 'https://www.plwebnne.com/join/GUBUT',
                        bitunix: 'https://www.bitunix.com/register?inviteCode=717517',
                        xt: 'https://www.xt.com/zh-CN/accounts/register?ref=ZH9HWY',
                        bitget: 'https://partner.niftah.cn/bg/E7MZJV'
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
                        twitter: 'https://twitter.com/gubitrade',
                        discord: 'discord_link'
                    },
                    exchanges: {
                        gate: 'https://www.gatenode.cloud/signup/VLURVV9EVG?ref_type=103',
                        binance: 'https://accounts.maxweb.black/register?ref=1090079770',
                        okx: 'https://www.plwebnne.com/join/GUBUT',
                        bitunix: 'https://www.bitunix.com/register?inviteCode=717517',
                        xt: 'https://www.xt.com/zh-CN/accounts/register?ref=ZH9HWY',
                        bitget: 'https://partner.niftah.cn/bg/E7MZJV'
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

// 静态文件服务（必须放在所有API路由之后）
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
  const { generateArticlePage } = require('./generate-article');
  try {
    generateArticlePage(articleData);
    res.json({ success: true, message: 'Article file generated successfully' });
  } catch (error) {
    console.error('生成文章文件时出错:', error);
    res.status(500).json({ success: false, message: 'Failed to generate article file' });
  }
}

// 保存文章数据到articles.json
function saveArticleData(articleData, res) {
  // 读取现有的文章数据
  const articlesPath = path.join(__dirname, 'articles.json');
  fs.readFile(articlesPath, (err, data) => {
    if (err && err.code !== 'ENOENT') {
      console.error('[ERROR] 读取 articles.json 失败:', err);
      return res.status(500).json({ success: false, message: 'Failed to read articles data' });
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
    
    // 检查是否已存在相同ID的文章
    const existingIndex = articles.findIndex(article => article.id === articleData.id);
    if (existingIndex !== -1) {
      // 如果存在，更新文章
      articles[existingIndex] = articleData;
    } else {
      // 添加新文章到开头
      articles.unshift(articleData);
    }
    
    // 写入文件
    fs.writeFile(articlesPath, JSON.stringify(articles, null, 2), (writeErr) => {
      if (writeErr) {
        console.error('[ERROR] 保存文章数据失败:', writeErr);
        return res.status(500).json({ success: false, message: 'Failed to save article data' });
      }
      
      // 更新网站地图
      updateSitemapAfterChange(articles);
      
      // 保存成功后，执行build.js脚本重新生成文章页面
      const buildPath = path.join(__dirname, 'build.js');
      exec(`node "${buildPath}"`, (error, stdout, stderr) => {
        if (error) {
          console.error(`执行build.js时出错: ${error}`);
          return res.json({ 
            success: true, 
            message: 'Article data saved successfully, but failed to build pages' 
          });
        }
        console.log(`build.js执行成功: ${stdout}`);
        res.json({ 
          success: true, 
          message: 'Article data saved and pages built successfully' 
        });
      });
    });
  });
}

// 更新文章数据
function updateArticleData(articleData, res) {
  // 读取现有的文章数据
  const articlesPath = path.join(__dirname, 'articles.json');
  fs.readFile(articlesPath, (err, data) => {
    if (err && err.code !== 'ENOENT') {
      console.error('[ERROR] 读取 articles.json 失败:', err);
      return res.status(500).json({ success: false, message: 'Failed to read articles data' });
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
          console.error('[ERROR] 更新文章数据失败:', writeErr);
          return res.status(500).json({ success: false, message: 'Failed to update article data' });
        }
        
        // 更新网站地图
        updateSitemapAfterChange(articles);
        
        // 更新成功后，执行build.js脚本重新生成文章页面
        const buildPath = path.join(__dirname, 'build.js');
        exec(`node "${buildPath}"`, (error, stdout, stderr) => {
          if (error) {
            console.error(`执行build.js时出错: ${error}`);
            return res.json({ 
              success: true, 
              message: 'Article data updated successfully, but failed to build pages' 
            });
          }
          console.log(`build.js执行成功: ${stdout}`);
          res.json({ 
            success: true, 
            message: 'Article data updated and pages built successfully' 
          });
        });
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
      console.error('[ERROR] 读取 articles.json 失败:', err);
      return res.status(500).json({ success: false, message: 'Failed to read articles data' });
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
    const initialLength = articles.length;
    articles = articles.filter(article => article.id !== articleId);
    
    // 检查是否有文章被删除
    if (articles.length === initialLength) {
      return res.status(404).json({ success: false, message: 'Article not found' });
    }
    
    // 写入文件
    fs.writeFile(articlesPath, JSON.stringify(articles, null, 2), (writeErr) => {
      if (writeErr) {
        console.error('[ERROR] 删除文章数据失败:', writeErr);
        return res.status(500).json({ success: false, message: 'Failed to delete article data' });
      }
      
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
            return res.json({ 
              success: true, 
              message: 'Article data deleted successfully, but failed to build pages' 
            });
          }
          console.log(`build.js执行成功: ${stdout}`);
          
          res.json({ 
            success: true, 
            message: 'Article data deleted and pages rebuilt successfully' 
          });
        });
      });
    });
  });
}

// 在文章变更后更新网站地图
function updateSitemapAfterChange(articles) {
    // 查询所有策略
    const query = 'SELECT * FROM strategies ORDER BY created_at DESC';
    
    db.query(query, (err, strategies) => {
        if (err) {
            console.error('查询策略失败:', err);
            // 即使策略查询失败，也更新网站地图（只包含文章）
            updateSitemap(articles, []);
        } else {
            // 使用文章和策略数据更新网站地图
            updateSitemap(articles, strategies);
        }
    });
}

// 在策略变更后更新网站地图
function updateSitemapAfterStrategyChange() {
    // 查询所有文章
    const articlesPath = path.join(__dirname, 'articles.json');
    
    fs.readFile(articlesPath, (err, data) => {
        let articles = [];
        if (!err && data) {
            try {
                articles = JSON.parse(data);
            } catch (parseErr) {
                console.error('[ERROR] 解析 articles.json 失败:', parseErr);
            }
        }
        
        // 查询所有策略
        const query = 'SELECT * FROM strategies ORDER BY created_at DESC';
        db.query(query, (err, strategies) => {
            if (err) {
                console.error('查询策略失败:', err);
                // 即使策略查询失败，也更新网站地图（只包含文章）
                updateSitemap(articles, []);
            } else {
                // 使用文章和策略数据更新网站地图
                updateSitemap(articles, strategies);
            }
        });
    });
}

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
  console.log(`  GET /api/users`);
  console.log(`  POST /api/users`);
  console.log(`  PUT /api/users/{id}`);
  console.log(`  DELETE /api/users/{id}`);
  console.log(`  GET /api/strategies`);
  console.log(`  POST /api/strategies`);
  console.log(`  PUT /api/strategies/{id}`);
  console.log(`  DELETE /api/strategies/{id}`);
  
  // 初始化数据库
  initializeDatabase();
});