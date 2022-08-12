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

    # класс модели истории пользователя
    class HistoryUser:

        def __init__(self, id, login_time, ip, port) -> None:
            self.user = id
            self.login_time = login_time
            self.ip = ip
            self.port = port

        def __repr__(self) -> str:
            return f'<{self.user} / {self.login_time} / {self.ip} / {self.port}>'


    def __init__(self) -> None:
        
        # путь для хранения файла базы данных
        path_dir = os.path.dirname(os.path.abspath(__file__))
        self.engine = create_engine(f'sqlite:///{path_dir}/server_data.db', 
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


        # таблица для истории пользователей
        history_users_table = Table('history_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('users.id')),
            Column('login_time', DateTime),
            Column('ip', String),
            Column('port', Integer)
        )

        # создаём таблицы
        self.metadata.create_all(self.engine)

        # связываем классы с таблицами
        mapper(self.User, users_table)
        mapper(self.ActiveUser, active_users_table)
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

        # создаём запись для таблицы history_users
        history_user = self.HistoryUser(user.id, datetime.datetime.now(), ip, port)
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

    # метод для получения истории пользователя или всех пользователей
    def history(self, user_name=None):
        # получаем все данные из таблицы 
        rezult = self.session.query(self.User.name,
                                    self.HistoryUser.login_time,
                                    self.HistoryUser.ip,
                                    self.HistoryUser.port
                                    ).join(self.User)
        # если указано имя - фильтруем результат
        if user_name:
            return rezult.filter(self.User.name==user_name).all()
        return rezult.all()

        




if __name__ == '__main__':
    server_db = ServerDataBase()
    # server_db.add_user('Ivan', '00.0.00.0', '1111')
    # server_db.add_user('Petr', '1.1.1.1', '2222')
    # server_db.del_user_from_active('Petr')
    print(server_db.all_users_list())
    print(server_db.active_users_list())
    print(server_db.history())
    print(server_db.history('Petr'))
    print(server_db.history('asfaf'))

