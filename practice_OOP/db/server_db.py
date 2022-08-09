from importlib import invalidate_caches
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker
import datetime


class User:
    def __init__(self, name, last_login_time) -> None:
        self.name = name
        self.last_login_time = last_login_time

    def __repr__(self):
        return f'<User: {self.name} last login: {self.last_login_time}>'

invalidate_caches
engine = create_engine('sqlite:///practice_OOP/db/server_data.db', echo=True, pool_recycle=7200)
metadata = MetaData()

users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('last_login_time', String)
    )

metadata.create_all(engine)
mapper(User, users_table)

Session = sessionmaker(bind=engine)
sess = Session()


if __name__ == '__main__':
    user = User('Ivan', datetime.datetime.now())
    print(user)
    sess.add(user)
    sess.commit()

        

