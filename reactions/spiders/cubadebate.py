from datetime import datetime
import scrapy
from database import Article, Comment
from reactions.spiders.base import BaseSpider

class CubadebateSpider(BaseSpider):
    name = 'cubadebate'
    allowed_domains = ['cubadebate.cu']
    start_urls = ['http://www.cubadebate.cu']

    def parse(self, response):
        article_elements = response.css('#front-list > div')
        for article_element in article_elements:
            title = article_element.css('div.title a::text').get()
            if not title:
                continue
            url = article_element.css('div.title a::attr(href)').get()
            date_str = article_element.css('div.meta time::attr(datetime)').get()
            try:
                date = datetime.fromisoformat(date_str)
            except:
                date = None
            try:
                article = Article.select().where(Article.uid == url).get()
            except Article.DoesNotExist:
                article = Article(title=title, url=url, uid=url, source=self.name, date=date, visited_at=None)
                article.save()
            if not self.already_visited(article):
                article.visited_at = datetime.now()
                article.save()
                yield scrapy.Request(url, callback=self.parse_comments, meta={'article': article})
        
        next_page = response.css('div.wp-pagenavi a.nextpostslink::attr(href)').get()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)
        
    def parse_comments(self, response):
        article = response.meta['article']
        comment_elements = response.css('#comments li.comment')
        for comment_element in comment_elements:
            author = comment_element.css('div.commenttext cite strong::text').get()
            body = comment_element.css('div.commenttext p::text').get()
            uid = comment_element.css('::attr(id)').get()

            try:
                comment = Comment.select().where(Comment.uid == uid).get()
            except Comment.DoesNotExist:
                comment = Comment(article=article, uid=uid, author=author, body=body)
                comment.save()
            
            self.store_sentiment(comment)

        next_page = response.css('div.wp-commentpagenavi a.next::attr(href)').get()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse_comments, meta={'article': article})
        
