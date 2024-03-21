from peewee import *

from settings.settings import DATABASE, USER, PASSWORD, HOST, PORT

db = PostgresqlDatabase(
    DATABASE,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    autorollback=True
)


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db


class Users(BaseModel):
    created_at = DateTimeField()
    user_id = BigIntegerField()
    command = CharField(max_length=50)
    city = CharField(max_length=50)
    currency = CharField(max_length=50)
    date_in = DateTimeField()
    date_out = DateTimeField()
    min_distance = FloatField(null=True)
    max_distance = FloatField(null=True)
    price_min = IntegerField(null=True)
    price_max = IntegerField(null=True)

    class Meta:
        db_table = 'users'


class Hotels(BaseModel):
    user_id = BigIntegerField()
    hotel_info = CharField(max_length=800)
    photo = CharField(max_length=1500, null=True)
    command_id_id = ForeignKeyField(Users, on_delete='CASCADE')

    class Meta:
        db_table = 'hotels'
