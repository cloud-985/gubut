const fs = require('fs');
const path = require('path');
const { updateArticlesJson } = require('./generate-article');

// 指定new文件夹路径
const newDir = path.join(__dirname, 'new');

/**
 * 从HTML文件中提取文章信息
 * @param {string} filePath - 文件路径
 * @returns {Object|null} - 文章对象或null
 */
function extractArticleInfo(filePath) {
    try {
        const htmlContent = fs.readFileSync(filePath, 'utf8');
        const fileName = path.basename(filePath);
        
        // 从文件名提取ID
        const idMatch = fileName.match(/article-([\d\w-]+)\.html/);
        const id = idMatch ? idMatch[1] : Math.random().toString(36).substr(2, 9);
        
        // 提取标题
        const titleMatch = htmlContent.match(/<h1[^>]*>(.*?)<\/h1>/);
        const title = titleMatch ? titleMatch[1].trim() : '无标题文章';
        
        // 提取日期
        const dateMatch = htmlContent.match(/<div\s+class="article-meta"[^>]*>[\s\S]*?([\d]{4}-[\d]{2}-[\d]{2})/);
        const date = dateMatch ? dateMatch[1] : new Date().toISOString().split('T')[0];
        
        // 提取文章内容（在article-body标签内）
        const contentMatch = htmlContent.match(/<div\s+class="article-body"[^>]*>([\s\S]*?)<\/div>/);
        const content = contentMatch ? contentMatch[1].trim() : '';
        
        return {
            id,
            title,
            date,
            content
        };
    } catch (error) {
        console.error(`提取文件 ${filePath} 信息失败:`, error);
        return null;
    }
}

/**
 * 从new文件夹读取所有文章并更新articles.json
 */
function main() {
    console.log('开始从new文件夹读取文章并重新生成articles.json文件...');
    
    // 清空现有的articles.json文件
    const articlesJsonPath = path.join(__dirname, 'articles.json');
    fs.writeFileSync(articlesJsonPath, JSON.stringify([], null, 2), 'utf8');
    console.log('已清空现有的articles.json文件');
    
    // 获取new文件夹中的所有HTML文件
    try {
        const files = fs.readdirSync(newDir).filter(file => file.endsWith('.html'));
        console.log(`找到 ${files.length} 篇文章，开始处理...`);
        
        let successCount = 0;
        
        for (const file of files) {
            const filePath = path.join(newDir, file);
            const articleInfo = extractArticleInfo(filePath);
            
            if (articleInfo) {
                // 使用修改后的updateArticlesJson函数处理文章
                updateArticlesJson(articleInfo);
                console.log(`✓ 成功处理: ${articleInfo.title}`);
                successCount++;
            }
        }
        
        console.log(`\n✅ 处理完成！成功处理了 ${successCount} 篇文章，所有文章内容已只保留前50个文字。`);
    } catch (error) {
        console.error('读取new文件夹失败:', error);
    }
}

main();