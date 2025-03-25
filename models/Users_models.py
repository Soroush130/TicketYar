from peewee import *
import datetime
from peewee import MySQLDatabase, Model, CharField

# Connect to the MySQL database
db = MySQLDatabase('jimmy',
                   user='root',
                   password='mfApsgdPdGuBnioj',
                   host='services.gen5.chabokan.net',
                   port=44104)

# db = SqliteDatabase('TicketYar.db')

class User(Model):
    username = CharField(unique=True)
    user_id = CharField(unique=True)
    first_name = CharField(null=True, default="")
    last_name = CharField(null=True, default="")  # Use default="" instead of None
    language_code = CharField(null=True, default="unknown")
    join_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        
try:
    db.connect()
    db.create_tables([User])
except Exception as e:
    print(f"Database connection error: {e}")
finally:
    if not db.is_closed():
        db.close()


