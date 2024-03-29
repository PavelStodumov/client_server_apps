import sys
import time
import socket
import logging
import threading
from common.variables import *
from common.utils import send_message, get_message

log = logging.getLogger('app.client')


def create_message(account_name='guest', to_user=None, text=None):
    '''
    Функция создаёт сообщение. Возвращает словарь.
    '''
    # если текс не передаётся, отправляется сообщение - приветствие
    if not text:
        return {
            ACTION: PRESENCE,
            TIME: time.strftime('%d.%m.%Y %H:%M:%S', time.localtime()),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
    # если клиент заходит с именем, отправим на сервер информацию
    elif account_name != 'guest' and not text:
        return {
            ACTION: 'intro',
            TIME: time.strftime('%d.%m.%Y %H:%M:%S', time.localtime()),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
    else:
        return {
            ACTION: 'message',
            TIME: time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()),
            USER: {
                ACCOUNT_NAME: account_name,
            },
            'to_user': to_user,
            'text': text
        }

# Поток, принимающий сообщения


def listen_thr(ip, port, username):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
        log.info(f'Клиент запущен с ip {ip}, port {port}')
        stream.connect((ip, port))
        # отправляем информацию о клиенте
        send_message(stream, create_message(account_name=username))
        while True:
            resp = get_message(stream)
            print(resp['text'])
            if resp['text'] == 'exit':
                break

# Поток, отправляющий сообщения


def send_thr(ip, port, username):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
        log.info(f'Клиент запущен с ip {ip}, port {port}')
        stream.connect((ip, port))
        # отправляем информацию о клиенте
        send_message(stream, create_message(account_name=username))
        while True:

            message = input('Введите [имя получателя]: [сообщение]: ')
            if ':' in message:
                to_username = message.split(':')[0].strip()
                text = ''.join(message.split(':')[1:]).strip()
            else:
                to_username = None
                text = message
            ready_message = create_message(
                account_name=username, to_user=to_username, text=text)
            send_message(stream, ready_message)


def main():
    '''
    Скрипт клиента запускаестя с необязательными аргументами:
        -р номер порта клиента(по умолчанию [7777])
        -а ip адрес клиента(по умолчанию [127.0.0.1])
        -u, --user имя клиента(по умолчанию [guest])
    '''
    try:
        port = int(sys.argv[sys.argv.index('-p') + 1]
                   ) if '-p' in sys.argv else DEFAULT_PORT
        if not 1024 < port < 65535:
            raise ValueError
    except:
        log.warning('Введён некорректный порт. Клиент не запущен')
        sys.exit(1)
    ip = sys.argv[sys.argv.index('-a') + 1] if '-a' in sys.argv else DEFAULT_IP

    if '-u' in sys.argv:
        username = sys.argv[sys.argv.index('-u') + 1]
    elif '--user' in sys.argv:
        username = sys.argv[sys.argv.index('--user') + 1]
    else:
        username = 'guest'

    THR_LISTEN = threading.Thread(target=listen_thr, args=(ip, port, username))
    THR_SEND = threading.Thread(target=send_thr, args=(ip, port, username))

    THR_LISTEN.start()
    THR_SEND.start()


if __name__ == '__main__':
    main()
