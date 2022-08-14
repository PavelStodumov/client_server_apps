from unicodedata import name
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, String, Integer, DateTime, MetaData, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker
import datetime
import os

class ServerDataBase:
    # класс - модель пользователя
    class User:
        def __init__(self, name, last_login_time) -> None:
            self.name = name
            self.last_login_time = last_login_time

        def __repr__(self):
            return f'<User: {self.name} last login: {self.last_login_time}>'

    # класс модели активных пользователей
    class ActiveUser:
        def __init__(self, id, login_time, ip, port) -> None:
            self.user = id
            self.login_time = login_time
            self.ip = ip
            self.port = port

        def __repr__(self) -> str:
            return f'<{self.user} / {self.login_time} / {self.ip} / {self.port}>'

    # класс модели истории входов пользователя
    class HistoryLoginUser:
        def __init__(self, id, login_time, ip, port) -> None:
            self.user = id
            self.login_time = login_time
            self.ip = ip
            self.port = port

        def __repr__(self) -> str:
            return f'<{self.user} / {self.login_time} / {self.ip} / {self.port}>'

    # класс модели контактов пользователя
    class ContactsUser:
        def __init__(self, user_id, contact_id):
            self.user = user_id
            self.contact = contact_id

        def __repr__(self) -> str:
            return f'<{self.user} - {self.contact}'

    # класс модели истории пользователя
    class HistoryUser:
        def __init__(self, user_id, message_in, message_out):
            self.user = user_id
            self.message_in = message_in
            self.message_out = message_out
            

    


    def __init__(self, 
                path=os.path.dirname(os.path.abspath(__file__))) -> None:
        
        # путь для хранения файла базы данных
        # по умолчанию местоположение файла
        self.engine = create_engine(f'sqlite:///{path}/server_data.db3', 
                                    echo=False, 
                                    pool_recycle=7200,
                                    connect_args={'check_same_thread': False}
                                    )
        self.metadata = MetaData()


        # таблица для моделей пользователей
        users_table = Table('users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String, unique=True),
            Column('last_login_time', DateTime)
        )

        # таблица для активных пользователей
        active_users_table = Table('active_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('users.id'), unique=True),
            Column('login_time', DateTime),
            Column('ip', String),
            Column('port', Integer)
        )


        # таблица для истории входа пользователей
        history_login_users_table = Table('history_login_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('users.id')),
            Column('login_time', DateTime),
            Column('ip', String),
            Column('port', Integer)
        )

        # таблица контактов
        contacts_users_table = Table('contacts_users', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('user', ForeignKey('users.id')),
                                Column('contact', ForeignKey('users.id'))
                                )

        # таблица истории пользователей
        history_users_table = Table('history_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('users.id'), unique=True),
            Column('message_in', Integer),
            Column('message_out', Integer)
        )

        # создаём таблицы
        self.metadata.create_all(self.engine)

        # связываем классы с таблицами
        mapper(self.User, users_table)
        mapper(self.ActiveUser, active_users_table)
        mapper(self.HistoryLoginUser, history_login_users_table)
        mapper(self.ContactsUser, contacts_users_table)
        mapper(self.HistoryUser, history_users_table)

        # создаём сессию
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # очищаем таблицу активных пользователей
        self.session.query(self.ActiveUser).delete()
        self.session.commit()

    # метод записывает пользователя в базу
    def add_user(self, name, ip, port):
        # ищем в таблице users пользователя по имени
        user = self.session.query(self.User).filter_by(name=name).first()
        # если пользователь есть - меняем время последнего входа
        if user:
            user.last_login_time = datetime.datetime.now()
        # если пользователя нет, создаём и записываем в базу
        else:
            user = self.User(name, datetime.datetime.now())
            self.session.add(user)
        # сохраняем изменения
        self.session.commit()

        # создаём запись для таблицы active_users

        if not self.session.query(self.ActiveUser).filter_by(user=user.id).first():
            active_user = self.ActiveUser(user.id, datetime.datetime.now(), ip, port)
            # добавляем в таблицу 
            self.session.add(active_user)

        # создаём запись для таблицы history_login_users
        history_login_user = self.HistoryLoginUser(user.id, datetime.datetime.now(), ip, port)
        self.session.add(history_login_user)

        # создаём запись для таблицы history_users
        if not self.session.query(self.HistoryUser).filter_by(user=user.id):
            history_user = self.HistoryUser(user.id, 0, 0)
            self.session.add(history_user)

        # сохраняем изменения
        self.session.commit()

    # метод удаляет пользователя из таблицы active_users
    def del_user_from_active(self, name):
        # находим пользователя по имени в таблице users
        user = self.session.query(self.User).filter_by(name=name).first()
        # находим запись в таблице active_users по id пользователя
        deactive = self.session.query(self.ActiveUser).filter_by(user=user.id)
        # удаляем запись
        deactive.delete()
        # сохраняем изменения
        self.session.commit()    

    # метод возвращает список всех пользователей
    def all_users_list(self):
        # выбранные поля попадут в кортеж 
        return self.session.query(self.User.name, self.User.last_login_time).all()

    # метод возвращает список активных пользователей
    def active_users_list(self):
        # запрашиваем данные из двух таблиц
        rezult = self.session.query(self.User.name,
                                    self.ActiveUser.login_time,
                                    self.ActiveUser.ip,
                                    self.ActiveUser.port,
                                    # объединяем данные
                                    ).join(self.User)
        return rezult.all()

    # метод для получения истории входов пользователя или всех пользователей
    def history(self, user_name=None):
        # получаем все данные из таблицы 
        rezult = self.session.query(self.User.name,
                                    self.HistoryLoginUser.login_time,
                                    self.HistoryLoginUser.ip,
                                    self.HistoryLoginUser.port
                                    ).join(self.User)
        # если указано имя - фильтруем результат
        if user_name:
            return rezult.filter(self.User.name==user_name).all()
        return rezult.all()

    # метод для записи истории сообщений в базу
    def messaging(self, sender, recipient):
        # получаем id отправителя и получателя
        send = self.session.query(self.User).filter_by(name=sender).first().id
        recip = self.session.query(self.User).filter_by(name=recipient).first().id
        # получаем записи из истории отправителя и получателя
        # для отправителя получаем счётчик отправленных сообщений и увеличиваем счётчики на 1
        self.session.query(self.HistoryUser).filter_by(user=send).first().message_out += 1
        # для принимающего получаем счётчик принятых сообщений и увеличиваем счётчики на 1
        self.session.query(self.HistoryUser).filter_by(user=recip).first().message_in += 1

        # сохраняем
        self.session.commit()

    # метод для просмотра истории пользователя
    def get_history_user(self, user):

        user_id = self.session.query(self.User).filter_by(name=user).first().id

        history = self.session.query(self.HistoryUser.message_in,
                                    self.HistoryUser.message_out).filter_by(user=user_id).first()
        # возвращаем кортеж (получено, отправлено)
        return history


        
    # метод для добавления контакта пользователю
    def add_contact(self, user, contact):
        # получаем пользователя, которого хотят добавить
        _contact = self.session.query(self.User).filter_by(name=contact).first()
        # если он существует, получаем id его и пользователя, который его добавляет
        if _contact:
            contact_id = _contact.id
            user_id = self.session.query(self.User).filter_by(name=user).first().id
            # проверяем, нет ли в базе такой записи, если нет, создаём, записываем
            if not self.session.query(self.ContactsUser).filter_by(user=user_id, contact=contact_id).first():
                user_contact = self.ContactsUser(user_id, contact_id)
                self.session.add(user_contact)
                self.session.commit()
            else:
                print(f'Пользователь {contact} уже в списке ваших контактов')
        else:
            print(f'Пользователя {contact} не существует')

    # метод для удаления контакта пользователя
    def del_contact(self, user, contact):
        # получаем запись о контакте, если она есть
        _contact = self.session.query(self.User).filter_by(name=contact).first()
        if _contact:
            contact_id = _contact.id
            user_id = self.session.query(self.User).filter_by(name=user).first().id
            row = self.session.query(self.ContactsUser).filter_by(user=user_id, contact=contact_id).first()
            if row:
                self.session.delete(row)
                self.session.commit()
                print(f'Пользователь {contact} был удалён из списка ваших контактов')
            else:
                print(f'Пользователя {contact} нет в списке ваших контактов')
        else:
            print(f'Пользователя {contact} не существует')

    # метод для просмотра контактов пользователя
    def contacts(self, user):
        user = self.session.query(self.User).filter_by(name=user).first()

        contacts = self.session.query(self.ContactsUser.contact, self.User.name).filter_by(user=user.id).\
            join(self.User, self.ContactsUser.contact == self.User.id).all()

        return [name[1] for name in contacts]

    # Функция возвращает количество переданных и полученных сообщений
    def message_history(self):
        query = self.session.query(
            self.User.name,
            self.User.last_login_time,
            self.HistoryUser.message_out,
            self.HistoryUser.message_in,
        ).join(self.User)
        # Возвращаем список кортежей
        return query.all()




if __name__ == '__main__':
    server_db = ServerDataBase()
    server_db.add_user('Ivan', '00.0.00.0', '1111')
    server_db.add_user('Petr', '1.1.1.1', '2222')
    server_db.add_user('pavel', '2.2.2.2', 4321)
    # server_db.del_user_from_active('Petr')
    print('+'*50)
    print(server_db.all_users_list())
    print('+'*50)
    print(server_db.active_users_list())
    print('+'*50)
    print(server_db.history())
    print('+'*50)
    print(server_db.history('Petr'))
    server_db.add_contact('Petr', 'pavel')
    server_db.add_contact('Petr', 'pavl')
    print('+'*50)
    server_db.messaging('pavel', 'Petr')
    print('+'*50)
    server_db.del_contact('Petr', 'Ivan')    
    server_db.del_contact('Petr', 'pavl')    
    # server_db.del_contact('Petr', 'pavel')
    print(server_db.get_history_user('pavel'))  
    print(server_db.contacts('Petr'))
    print(server_db.message_history())



