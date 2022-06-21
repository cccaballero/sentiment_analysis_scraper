from peewee import SqliteDatabase, Model, CharField, TextField, ForeignKeyField, FloatField, DateTimeField

db = SqliteDatabase('data.db')

class Article(Model):
    uid = CharField()
    title = CharField()
    source = CharField()
    url = CharField()
    date = DateTimeField(null=True)
    visited_at = DateTimeField(null=True)

    class Meta:
        database = db

class Comment(Model):
    article = ForeignKeyField(Article, backref='comments')
    uid = CharField()
    author = CharField()
    body = TextField()

    class Meta:
        database = db

class Sentiment(Model):
    comment = ForeignKeyField(Comment, backref='sentiments')
    output = CharField()
    pos = FloatField()
    neg = FloatField()
    neu = FloatField()

    class Meta:
        database = db

db.create_tables([Article, Comment, Sentiment])
