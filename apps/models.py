from peewee import *
import datetime


db = SqliteDatabase('my_database.db')

class BaseModel(Model):

    class Meta:
        database = db


class Item(BaseModel):
    title = CharField()
    description = TextField()
    filename = CharField()
    created_date = DateTimeField(default=datetime.datetime.now)
    