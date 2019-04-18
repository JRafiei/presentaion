from peewee import *
import datetime


db = SqliteDatabase('my_database.db')

class BaseModel(Model):

    class Meta:
        database = db
