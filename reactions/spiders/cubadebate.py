from datetime import datetime, timedelta
from unicodedata import name
import scrapy

from pysentimiento import create_analyzer

from database import Article, Comment, Sentiment

from analyze import sentiment_analyzer

VISITING_TIME = 10

class CubadebateSpider(scrapy.Spider):
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
            if not article.visited_at or article.visited_at < datetime.now() - timedelta(days=VISITING_TIME):
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
            
            try:
                sentiment = Sentiment.select().where(Sentiment.comment == comment).get()
            except Sentiment.DoesNotExist:
                output = sentiment_analyzer.predict(body)
                sentiment = Sentiment(comment=comment, output=output.output, pos=output.probas["POS"], neg=output.probas["NEG"], neu=output.probas["NEU"])
                sentiment.save()

        next_page = response.css('div.wp-commentpagenavi a.next::attr(href)').get()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse_comments, meta={'article': article})
        
