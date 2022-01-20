from peewee import *
import datetime


db = SqliteDatabase('my_database.db')

class BaseModel(Model):

    class Meta:
        database = db


class Presentation(BaseModel):
    title = CharField()
    icon = CharField()

    def get_url(self):
        return f'/present/{self.id}'


class Item(BaseModel):
    presentation = ForeignKeyField(Presentation, backref='items', null=True)
    title = CharField()
    description = TextField()
    filename = CharField()
    order = SmallIntegerField(null=True)
    created_date = DateTimeField(default=datetime.datetime.now)
    