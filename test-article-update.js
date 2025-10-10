const fs = require('fs');
const path = require('path');
const { updateArticlesJson } = require('./generate-article');

// 创建一个模拟的测试文章
const testArticle = {
    id: 'test-article-' + Date.now(),
    title: '测试文章：验证内容处理功能',
    date: new Date().toISOString().split('T')[0],
    content: `
        <p>这是一篇测试文章，用于验证generate-article.js中的内容处理功能。</p>
        <p>这篇文章包含<strong>HTML标签</strong>、<em>格式化文本</em>和图片：</p>
        <img src="../img/logo.png" alt="Logo图片">
        <p>我们需要确保在保存到JSON文件时，只保留纯文本内容的前50个字符，并且不包含任何HTML标签、图片或其他代码。</p>
        <div class="some-class">这是一个带有class属性的div标签</div>
    `
};

function main() {
    console.log('开始测试文章内容处理功能...');
    console.log('原始文章内容:', testArticle.content);
    
    // 调用updateArticlesJson函数
    updateArticlesJson(testArticle);
    
    // 读取更新后的articles.json文件
    const articlesJsonPath = path.join(__dirname, 'articles.json');
    const articlesData = fs.readFileSync(articlesJsonPath, 'utf8');
    const articles = JSON.parse(articlesData);
    
    // 查找刚刚添加的测试文章
    const addedArticle = articles.find(article => article.id === testArticle.id);
    
    if (addedArticle) {
        console.log('\n测试结果:');
        console.log('处理后的文章内容:', addedArticle.content);
        console.log('内容长度:', addedArticle.content.length, '字符');
        
        // 验证内容是否符合要求
        if (addedArticle.content.length <= 53 && // 50个字符加上可能的'...'
            !/<[^>]*>/.test(addedArticle.content)) { // 没有HTML标签
            console.log('\n✅ 测试通过！文章内容已正确处理，只保留前50个文字，没有HTML标签和图片。');
        } else {
            console.log('\n❌ 测试失败！文章内容处理不符合要求。');
        }
    } else {
        console.log('\n❌ 测试失败！未能在articles.json中找到测试文章。');
    }
}

main();