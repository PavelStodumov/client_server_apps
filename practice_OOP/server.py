import socket
import sys
import argparse
import json
import logging
import select
import threading
import time
import logs.config_server_log
from errors import IncorrectDataRecivedError
from common.variables import *
from common.utils import *
from common.descriptors import ValidationPort
from decos import log
from common.metaclasses import ServerVerifier
from db.server_db import ServerDataBase
import tabulate

# Инициализация логирования сервера.
logger = logging.getLogger('server_dist')

# Флаг, что был подключён новый пользователь, нужен чтобы не мучать BD
# постоянными запросами на обновление
new_connection = False
conflag_lock = threading.Lock()

# функция для получения ключа словаря по его значению
def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k

# Парсер аргументов командной строки.
@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


# Основной класс сервера
class Server(threading.Thread, metaclass=ServerVerifier):
    # Дескрипттор для валидации номера порта
    port = ValidationPort()
    
    def __init__(self, listen_address, listen_port, db):

        # Параметры подключения
        self.addr = listen_address
        self.port = listen_port

        # база данных
        self.db = db

        # Список подключённых клиентов.
        self.clients = []

        # Список сообщений на отправку.
        self.messages = []

        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.names = dict()

        # конструктор родителей
        super().__init__()

    def init_socket(self):
        logger.info(
            f'Запущен сервер, порт для подключений: {self.port}, '
            f'адрес с которого принимаются подключения: {self.addr}. '
            f'Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        # Начинаем слушать сокет.
        self.sock = transport
        self.sock.listen()

    def run(self):
        # Инициализация Сокета
        self.init_socket()

        # Основной цикл программы сервера
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
                    except:
                        logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        # удаляем клиента из базы активных
                        client_name = get_key(self.names, client_with_message)
                        self.db.del_user_from_active(client_name)
                        self.clients.remove(client_with_message)
                        del self.names[client_name]

            # Если есть сообщения, обрабатываем каждое.
            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except Exception as e:
                    logger.info(f'Связь с клиентом с именем '
                                f'{message[DESTINATION]} была потеряна, '
                                f' ошибка {e}')
                    # удаляем клиента из базы активных
                    self.db.del_user_from_active(message[DESTINATION])

                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    # Функция адресной отправки сообщения определённому клиенту.
    # Принимает словарь сообщение, список зарегистрированных
    # пользователей и слушающие сокеты. Ничего не возвращает.
    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and \
                self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                        f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names \
                and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован '
                f'на сервере, отправка сообщения невозможна.')

    # Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
    # проверяет корректность, отправляет словарь-ответ в случае необходимости.
    def process_client_message(self, message, client):
        global new_connection
        logger.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE \
                and TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован, регистрируем,
            # иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                # записываем пользователя в базу данных
                client_ip = client.getpeername()[0]
                client_port = client.getpeername()[1]
                self.db.add_user(name=message[USER][ACCOUNT_NAME], ip=client_ip, port=client_port)

                send_message(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and DESTINATION in message \
                and TIME in message \
                and SENDER in message \
                and MESSAGE_TEXT in message:
            self.messages.append(message)
            self.db.messaging(message[SENDER], message[DESTINATION])
            return
        # Если клиент выходит
        elif ACTION in message \
                and message[ACTION] == EXIT \
                and ACCOUNT_NAME in message:
            # удаляем из базы из активных юзеров
            self.db.del_user_from_active(message[ACCOUNT_NAME])
            ####################################################
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        # если клиент добавляет в список контактов
        elif ACTION in message and message[ACTION] == 'add_contact'\
                    and USER in message\
                    and ACCOUNT_NAME in message:    
            self.db.add_contact(message[USER], message[ACCOUNT_NAME])
            answ = RESPONSE_200
            answ=[INFO] = f'Пользователь {message[ACCOUNT_NAME]} добавлен в список контактов'
            send_message(client, answ)
            return
        # если клиент удаляет из списка контактов
        elif ACTION in message and message[ACTION] == 'del_contact'\
                and USER in message \
                and ACCOUNT_NAME in message:
            self.db.del_contact(message[USER], message[ACCOUNT_NAME])
            answ = RESPONSE_200
            answ=[INFO] = f'Пользователь {message[ACCOUNT_NAME]} удалён из списка контактов'
            send_message(client, answ)
            return
        # если клиеннт запрашивает список контактов
        elif ACTION in message and message[ACTION] == 'get_contacts' and USER in message:
            contacts = self.db.contacts(message[USER])
            answ = RESPONSE_202
            answ[INFO] = contacts
            send_message(client, answ)
            return
        # если клиент запрашивает всех пользователей
        elif ACTION in message and message[ACTION] == 'all_users':
            all_users = [u[0] for u in self.db.all_users_list()]
            print(f'all users {all_users}')
            answ = RESPONSE_202
            print(answ)
            answ[INFO] = all_users
            print(f'answ {answ}')
            send_message(client, answ)
            return
        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return

def show_help():
    print('Доступные команды:')
    print('all_users - список всех пользователей')
    print('active_users - список активных пользователей')
    print('login_history [user] - история входа пользователей или [пользователя]')
    print('help - справка о командах')
    print('exit - остановить сервер')


def main():
    # Загрузка параметров командной строки, если нет параметров,
    # то задаём значения по умолчанию.
    listen_address, listen_port = arg_parser()
    # создание экземпляра класса - базы данных
    db = ServerDataBase()
    # Создание экземпляра класса - сервера.
    server = Server(listen_address, listen_port, db)

    server.daemon = True
    server.start()

   



    while True:
        command = input('Введите команду: ')
        if command == 'exit':
            if input('Вы уверены, что хотите остановить сервер? y/n :') == 'y':
                break
        elif command == 'help':
            show_help()
        elif command == 'all_users':
            headers = ['user', 'last_login_time']
            print(tabulate.tabulate(server.db.all_users_list(), headers=headers, tablefmt='grid'))
        elif command == 'active_users':
            headers = ['user', 'last_login_time', 'ip', 'port']
            print(tabulate.tabulate(server.db.active_users_list(), headers=headers, tablefmt='grid'))
        elif command.startswith('login_history'):
            headers = ['user', 'last_login_time', 'ip', 'port']
            try:
                username = command.split(' ')[1]
                print(tabulate.tabulate(server.db.history(username), headers=headers, tablefmt='grid'))
            except IndexError:
                print(tabulate.tabulate(server.db.history(), headers=headers, tablefmt='grid'))
        else:
            print('Неизвестная команда')



if __name__ == '__main__':
    show_help()
    main()
