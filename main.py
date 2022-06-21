import click
from peewee import JOIN
from scrapy.cmdline import execute
from database import Sentiment, Comment, Article


@click.group()
def sentiment_analysis():
    pass

@sentiment_analysis.command(help='Start scraping and processing')
def scrap():
    execute(['scrapy', 'runspider', 'reactions/spiders/cubadebate.py'])

@sentiment_analysis.command(help='find articles in database')
@click.argument('search_term')
def find(search_term):
    query = Article.select().where(Article.title.contains(search_term))
    for article in query:
        print(article.title, article.url)


@sentiment_analysis.command(help='query an article comments sentiment information')
@click.argument('article_url')
def query(article_url):
    base_query = Sentiment.select().join(Comment, JOIN.LEFT_OUTER).join(Article, JOIN.LEFT_OUTER).where(Article.url == article_url)

    if not base_query.exists():
        print('No sentiment data for this article')
        exit(1)

    sentiments_pos = base_query.where(Sentiment.output == 'POS')
    sentiments_neg = base_query.where(Sentiment.output == 'NEG')
    sentiments_neu = base_query.where(Sentiment.output == 'NEU')

    print("Positive:", sentiments_pos.count())
    print("Negative:", sentiments_neg.count())
    print("Neutral:", sentiments_neu.count())

if __name__ == '__main__':
    sentiment_analysis()
