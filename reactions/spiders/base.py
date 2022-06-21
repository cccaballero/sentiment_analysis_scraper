from datetime import datetime, timedelta
import scrapy
from database import Sentiment
from analyze import sentiment_analyzer


class BaseSpider(scrapy.Spider):
    name = None
    allowed_domains = None
    start_urls = None
    visiting_time = 10

    def already_visited(self, article):
        if article.visited_at:
            return article.visited_at > (datetime.now() - timedelta(days=self.visiting_time))
        return False

    def predictSentiment(self, body):
        return sentiment_analyzer.predict(body)

    def store_sentiment(self, comment):
        try:
            sentiment = Sentiment.select().where(Sentiment.comment == comment).get()
        except Sentiment.DoesNotExist:
            output = self.predictSentiment(comment.body)
            sentiment = Sentiment(comment=comment, output=output.output, pos=output.probas["POS"],
                                  neg=output.probas["NEG"], neu=output.probas["NEU"])
            sentiment.save()
        return sentiment

    def parse(self, response):
        raise NotImplementedError
        
    def parse_comments(self, response):
        raise NotImplementedError
        
