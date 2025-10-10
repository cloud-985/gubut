// 测试generate-article.js能否正确生成和更新articles.json文件
const { updateArticlesJson } = require('./generate-article.js');
const fs = require('fs');
const path = require('path');

// 创建一个测试文章对象
const testArticle = {
    id: 'test-' + Date.now(),
    title: '测试generate-article.js生成JSON功能',
    date: '2025-10-10',
    content: '<p>这是一篇<strong>测试文章</strong>，用于验证generate-article.js中的updateArticlesJson函数是否能正确提取纯文本内容。</p><img src="test.jpg" alt="测试图片">'
};

console.log('开始测试...');
console.log('测试文章原始内容:', testArticle.content);

// 调用updateArticlesJson函数
updateArticlesJson(testArticle);

// 读取并检查articles.json文件
const articlesJsonPath = path.join(__dirname, 'articles.json');
const articlesData = fs.readFileSync(articlesJsonPath, 'utf8');
const articles = JSON.parse(articlesData);

// 查找测试文章
const testArticleInJson = articles.find(article => article.id === testArticle.id);

if (testArticleInJson) {
    console.log('测试通过！测试文章已成功添加到articles.json');
    console.log('处理后的内容:', testArticleInJson.content);
    console.log('内容长度:', testArticleInJson.content.length);
    console.log('是否包含HTML标签:', /<[^>]*>/.test(testArticleInJson.content));
    
    // 清理：移除测试文章
    const updatedArticles = articles.filter(article => article.id !== testArticle.id);
    fs.writeFileSync(articlesJsonPath, JSON.stringify(updatedArticles, null, 2), 'utf8');
    console.log('测试完成，已清理测试数据');
} else {
    console.log('测试失败！测试文章未添加到articles.json');
}