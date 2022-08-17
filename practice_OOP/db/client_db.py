from datetime import datetime
from email import message
import os
import sqlalchemy
from sqlalchemy import create_engine, Table,DateTime, Text, Integer, String, MetaData, Column
from sqlalchemy.orm import mapper, sessionmaker


class ClientDatabase:

    # модель таблицы всех пользователей
    class Users:
        def __init__(self, user_name):
            self.name = user_name

    # модель списка контактов
    class Contacts:
        def __init__(self, contact_name):
            self.name = contact_name

    # модель истории сообщений
    class MessageHistory:
        def __init__(self, from_user, to_user, message) -> None:
            self.from_user = from_user
            self.to_user = to_user
            self.message = message
            self.date_time = datetime.now()

    def __init__(self, name):
        # для каждого клиента своя база данных
        # зададим путь по умолчанию
        path=os.path.dirname(os.path.abspath(__file__))
        # движок по имени клиента
        self.engine = create_engine(f'sqlite:///{path}/{name}_data.db3')

        self.metadata = MetaData()

        # Таблица всех пользователей
        users = Table('users', self.metadata,
                        Column('id', Integer, primary_key = True),
                        Column('name', String))
        
        # таблица контактов
        contacts = Table('contacts', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('name', String, unique=True))

        # таблица истории сообщений
        message_history = Table('message_history', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('from_user', String),
                                Column('to_user', String),
                                Column('message', Text),
                                Column('date_time', DateTime))

        self.metadata.create_all(self.engine)

        mapper(self.Users, users)
        mapper(self.Contacts, contacts)
        mapper(self.MessageHistory, message_history)

        # создаём сессию
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Необходимо очистить таблицу контактов, т.к. при запуске они подгружаются с сервера.
        self.session.query(self.Contacts).delete()
        self.session.commit()

    # метод добавления контактов
    def add_contact(self, name):
        # проверяем нет ли уже контакта в таблице
        if not self.session.query(self.Contacts).filter_by(name=name).first():
            contact = self.Contacts(name)
            self.session.add(contact)
            self.session.commit()

    # метод удаления контактов
    def del_contact(self, name):
        # проверим есть ли пользователь в списке контактов
        contact = self.session.query(self.Contacts).filter_by(name=name).first()
        if contact:
            self.session.delete(contact)
            self.session.commit()

    # метод возвращает список контактов
    def get_contacts(self):
        return [u[0] for u in self.session.query(self.Contacts.name).all()]

    # метод проверки пользователя в контактах
    def check_contact(self, user):
        if self.session.query(self.Contacts).filter_by(name=user).first():
            return True
        return False

    # метод добавления всех пользователей в таблицу
    def add_users(self, users_list):
        # актуальный список пользователей получаем с сервера
        # поэтому сначала удаляем имеющийся
        self.session.query(self.Users).delete()
        for user in users_list:
            _user = self.Users(user)
            self.session.add(_user)
        self.session.commit()

    # метод возвращает список всех пользователей
    def get_users(self):
        return [u[0] for u in self.session.query(self.Users.name).all()]

    # метод проверки пользователя во всех пользователях
    def check_user(self, user):
        if self.session.query(self.Users).filter_by(name=user).first():
            return True
        return False

    # метод добавляет в таблицу сообщение
    def add_message(self, from_user, to_user, text):
        message = self.MessageHistory(from_user, to_user, text)
        self.session.add(message)
        self.session.commit()

    # метод возвращает историю сообщений
    def get_message_history(self, from_user=None, to_user=None):
        rez = self.session.query(self.MessageHistory)
        if from_user:
            rez = rez.filter_by(from_user=from_user)
        if to_user:
            rez = rez.filter_by(to_user=to_user)
        return [(message.from_user, 
                message.to_user, 
                message.message,
                message.date_time) for message in rez.all()]

    

if __name__ == '__main__':
    db = ClientDatabase('test')
    users = ['one', 'two', 'three']
    db.add_users(users)
    print(db.get_users())
    db.add_contact('one')
    db.add_contact('two')
    # db.del_contact('one')
    print(db.get_contacts())
    db.add_message('test', 'one', 'jhdccdhjch')
    print(db.check_contact('jfjfj'))
    print(db.check_contact('one'))
    print(db.check_user('kjvr'))
    print(db.check_user('three'))
    print(db.get_message_history())
