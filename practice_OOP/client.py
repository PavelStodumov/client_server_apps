import sys
import json
import socket
import time
import dis
import argparse
import logging
import threading
import logs.config_client_log
from common.variables import *
from common.utils import *
from common.metaclasses import ClientVerifier
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from decos import log
from db.client_db import ClientDatabase

# Инициализация клиентского логера
logger = logging.getLogger('client_dist')

# Объект блокировки сокета и работы с базой данных
sock_lock = threading.Lock()
db_lock = threading.Lock()


# Класс формировки и отправки сообщений на сервер и взаимодействия с пользователем.
class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, db):
        self.account_name = account_name
        self.sock = sock
        # база данных
        self.db = db
        super().__init__()

    # Функция создаёт словарь с сообщением о выходе.
    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    # Функция запрашивает кому отправить сообщение и само сообщение, и отправляет полученные данные на сервер.
    def create_message(self):
        to = input('Введите получателя сообщения: ')
        
        # проверяем существование указанного пользователя
        with db_lock:
            if not self.db.check_user(to):
                logger.error(f'попытка отправить сообщение незарегистрированному пользователю {to}')
                return

        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        
        # сохраняем сообщение в базу
        with db_lock:
            self.db.add_message(self.account_name, to, message)

        # Необходимо дождаться освобождения сокета для отправки сообщения
        with sock_lock:
        
            try:
                send_message(self.sock, message_dict)
                logger.info(f'Отправлено сообщение для пользователя {to}')
            except:
                logger.critical('Потеряно соединение с сервером.')
                exit(1)

    # Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения
    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'contacts':
                with db_lock:
                    contacts = self.db.get_contacts()
                    for contact in contacts:
                        print(contact)
            elif command == 'add_contact':
                self.add_contact()
            elif command == 'del_contact':
                self.del_contact()
            elif command == 'history':
                self.show_history()
            
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_exit_message())
                except:
                    pass
                print('Завершение соединения.')
                logger.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    # Функция выводящяя справку по использованию.
    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('add_contact - добавить пользователя в контакты')
        print('del_contact - удалить пользователя из контактов')
        print('contacts - показать список контактов')
        print('users - показать список всех пользователей')
        print('history - показать историю сообщений')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    def show_history(self):
        ask = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
        with db_lock:
            if ask == 'in':
                history_list = self.db.get_message_history(to_user=self.account_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} '
                          f'от {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.db.get_message_history(from_user=self.account_name)
                for message in history_list:
                    print(f'\nСообщение пользователю: {message[1]} '
                          f'от {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]},'
                          f' пользователю {message[1]} '
                          f'от {message[3]}\n{message[2]}')

    # метод добавления контакта
    def add_contact(self):
        name = input('Кого вы хотите добавить в список контактов: ')
        # Проверка на наличие такого пользователя
        if self.db.check_user(name):
            with db_lock:
                self.db.add_contact(name)
            with sock_lock:
                try:
                    add_contant(self.sock, self.account_name, name)
                except ServerError:
                    logger.error('не удалось отправить информацию на сервер')
            

    # метод удаления контакта
    def del_contact(self):
        name = input('Кого вы хотите удалить из списка контактов: ')
        with db_lock:
            if self.db.check_contact(name):
                self.db.del_contact(name)
            else:
                logger.error('попытка удаления несуществующего контакта')          


# Класс-приёмник сообщений с сервера. Принимает сообщения, выводит в консоль.
class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, db):
        self.account_name = account_name
        self.sock = sock
        self.db = db
        super().__init__()

    # Основной цикл приёмника сообщений, принимает сообщения, выводит в консоль. Завершается при потере соединения.
    def run(self):
        while True:
            # Отдыхаем секунду и снова пробуем захватить сокет.
            # Если не сделать тут задержку,
            # то второй поток может достаточно долго ждать освобождения сокета.
            time.sleep(1)
            with sock_lock:
                try:
                    message = get_message(self.sock)
                except IncorrectDataRecivedError:
                    logger.error(f'Не удалось декодировать полученное сообщение.')
                except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                    logger.critical(f'Потеряно соединение с сервером.')
                    break
                # если сообщение корректное записываем в базу и выводим в консоль
                else:
                    if ACTION in message and message[ACTION] == MESSAGE\
                            and SENDER in message\
                            and DESTINATION in message \
                            and MESSAGE_TEXT in message\
                            and message[DESTINATION] == self.account_name:
                        print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                        # захватываем базу данных и записываем в неё сообщение
                        with db_lock:
                            try:
                                self.db.add_message(message[SENDER], self.account_name, message[MESSAGE_TEXT])
                            except Exception as e:
                                print(e)
                                logger.error('Ошибка работы с базой данных')
                        logger.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')

                    else:
                        logger.error(f'Получено некорректное сообщение с сервера: {message}')



# Функция генерирует запрос о присутствии клиента
@log
def create_presence(account_name):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


# Функция разбирает ответ сервера на сообщение о присутствии, возращает 200 если все ОК или генерирует исключение при\
# ошибке.
@log
def process_response_ans(message):
    logger.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


# Парсер аргументов коммандной строки
@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. Допустимы адреса с 1024 до 65535. Клиент завершается.')
        exit(1)

    return server_address, server_port, client_name

# запрос всех пользователей
def get_user_list(sock, username):
    logger.debug(f'Запрос списка пользователей {username}')
    req = {
        ACTION: 'all_users',
        TIME: time.time(),
        ACCOUNT_NAME: username
    }
    send_message(sock, req)
    ans = get_message(sock)
    logger.debug(f'получаем ответ {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[INFO]
    else:
        raise ServerError

# запрос списка контактов
def get_contact_list(sock, name):
    logger.debug(f'запрос списка контактов для пользователя {name}')
    req = {
        ACTION: 'get_contacts',
        TIME: time.time(),
        USER: name
    }
    send_message(sock, req)
    logger.debug(f'отправлен запрос {req}')
    ans = get_message(sock)
    logger.debug(f'получен ответ {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[INFO]
    else:
        raise ServerError

# добавление пользователя в контакты
def add_contant(sock, username, contactname):
    logger.debug(f'добавление в список контактов {contactname}')
    req = {
        ACTION: 'add_contact',
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contactname
    }
    send_message(sock, req)
    logger.debug(f'отправлен запрос {req}')
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        print(ans[INFO])
    else:
        raise ServerError('Ошибка создания контакта')

# удаление пользователя из контактов
def del_contant(sock, username, contactname):
    logger.debug(f'удаление из списка контактов {contactname}')
    req = {
        ACTION: 'del_contact',
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contactname
    }
    send_message(sock, req)
    logger.debug(f'отправлен запрос {req}')
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        print(ans[INFO])
    else:
        raise ServerError('Ошибка создания контакта')

# запуск базы данных
def db_load(sock, db, username):
    # загружаем список всех пользователей
    try:
        users_list = get_user_list(sock, username)
    except ServerError:
        print('Ошибка загрузки списка пользователей')
    else:

        db.add_users(users_list)
    
    # загружаем список контактов
    try:
        contacts = get_contact_list(sock, username)
    except ServerError:
        print('ошибка загрузки контактов')
    else:
        for contact in contacts:
            db.add_contact(contact)



def main():
    # Сообщаем о запуске
    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = arg_parser()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , '
        f'порт: {server_port}, имя пользователя: {client_name}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Таймаут 1 секунда, необходим для освобождения сокета.
        transport.settimeout(1)        
        
        
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_response_ans(get_message(transport))
        logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        logger.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        exit(1)
    else:
        # инициализация бд
        db = ClientDatabase(client_name)
        db_load(transport, db, client_name)


        # Если соединение с сервером установлено корректно,
        # запускаем поток взаимодействия с пользователем
        module_sender = ClientSender(client_name, transport, db)
        module_sender.daemon = True
        module_sender.start()
        logger.debug('Запущены процессы')
        # Если соединение с сервером установлено корректно, запускаем клиентский процесс приёма сообщений
        # module_reciver = ClientReader(client_name, transport, db)
        # module_reciver.daemon = True
        # module_reciver.start()

        # затем запускаем поток - приёмник сообщений.
        module_receiver = ClientReader(client_name, transport, db)
        module_receiver.daemon = True
        module_receiver.start()
        # # затем запускаем отправку сообщений и взаимодействие с пользователем.
        # module_sender = ClientSender(client_name, transport, db)
        # module_sender.daemon = True
        # module_sender.start()
        # logger.debug('Запущены процессы')

        # Watchdog основной цикл, если один из потоков завершён, то значит или потеряно соединение, или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках, достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
