from peewee import *
import datetime

db = SqliteDatabase('TicketYar.db')

class User(Model):
    username = CharField(unique=True)
    user_id = CharField(unique=True)
    first_name = CharField(null=True, default="")
    last_name = CharField(null=True, default="")  # Use default="" instead of None
    language_code = CharField(null=True, default="unknown")
    join_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        
db.connect()
db.create_tables([User])


