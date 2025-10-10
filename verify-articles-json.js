const fs = require('fs');
const path = require('path');

const articlesJsonPath = path.join(__dirname, 'articles.json');

function main() {
    try {
        // 读取articles.json文件
        const data = fs.readFileSync(articlesJsonPath, 'utf8');
        const articles = JSON.parse(data);
        
        console.log(`articles.json包含${articles.length}篇文章\n`);
        
        // 验证每篇文章的内容
        articles.forEach((article, index) => {
            console.log(`文章${index + 1}:`);
            console.log(`  ID: ${article.id}`);
            console.log(`  标题: ${article.title}`);
            console.log(`  日期: ${article.date}`);
            console.log(`  内容长度: ${article.content.length} 字符`);
            console.log(`  内容: "${article.content}"`);
            
            // 检查内容是否符合要求
            const hasHtmlTags = /<[^>]*>/.test(article.content);
            console.log(`  包含HTML标签: ${hasHtmlTags ? '是' : '否'}`);
            
            if (article.content.length <= 53 && !hasHtmlTags) {
                console.log('  ✓ 符合要求：内容长度不超过53字符，且不包含HTML标签');
            } else {
                console.log('  ✗ 不符合要求：内容超长或包含HTML标签');
            }
            console.log('---');
        });
        
        // 检查是否所有文章都符合要求
        const allValid = articles.every(article => 
            article.content.length <= 53 && !/<[^>]*>/.test(article.content)
        );
        
        if (allValid) {
            console.log('\n✅ 验证通过！所有文章的内容都只保留了前50个文字，没有包含图片和其他代码。');
        } else {
            console.log('\n❌ 验证失败！部分文章的内容不符合要求。');
        }
        
    } catch (error) {
        console.error('读取文件时出错:', error);
    }
}

main();