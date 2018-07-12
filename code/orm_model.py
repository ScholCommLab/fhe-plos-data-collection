# coding: utf-8

from peewee import *


class BaseModel(Model):
    """The base model which connects to our SQLite db"""
    class Meta:
        database = db


class Article(BaseModel):
    """ORM Model for academic articles"""
    id = IntegerField(primary_key=True)
    created_on = DateField()

    doi = TextField(unique=True)
    publication_date = DateField()
    title = TextField(null)
    # data seems to be incomplete... not sure about the other fields
    author = TextField(null=True)


class URL(BaseModel):
    """ORM Model for article URLs"""
    id = IntegerField(primary_key=True)
    articleID = ForeignKeyField(Article, backref="id")

    url = TextField()
    # might become relevant for URL crawlers
    is_duplicate = BooleanField(default=False)
    added_on = DateField(default=datetime.datetime.now)


class Query(BaseModel):
    """ORM Model for Graph API Queries"""
    id = IntegerField(primary_key=True)
    urlID = ForeignKeyField(URL, backref="id")

    queried_on = DateField()
    response_status = IntegerField()
    error_msg = TextField(null=True)


class GraphObject(BaseModel):
    """ORM Model for queried Graph Objects"""
    id = IntegerField(primary_key=True)  # og_id provided by FB
    queryID = ForeignKeyField(Query, backref="id")

    # URL that Facebook received - useful to double-check FB's internal heuristics
    fb_url = TextField(null=True)
    received_on = DateField()

    # OG object
    og_description = TextField(null=True)
    og_title = TextField(null=True)
    og_type = TextField(null=True)
    og_updated_time = DateField()

    # Engagement object
    reactions = IntegerField(default=0)
    shares = IntegerField(default=0)
    comments = IntegerField(default=0)
    plugin_comments = IntegerField(default=0)


class Event(BaseModel):
    """ORM Model for CED Events"""
