import sys
import logging
import select
from socket import *
from common.variables import *
from common.utils import *

log = logging.getLogger('app.server')


def response_message(message):
    log.info(f'Принято сообщение: {message}')
    if message[ACTION] == PRESENCE and message['user']['account_name'] == 'guest':
        return {
            RESPONSE: '200',
            'status': 'ok'
        }
    elif message[ACTION] == 'message':
        return message
    elif message[ACTION] == 'intro':
        return message
    return {
        RESPONSE: '400',
        'status': 'Bad request'
    }


def read_clients(r_clients, all_clients):
    # читаем сообщения от клиентов
    resp = {}
    for sock in r_clients:
        try:
            data = get_message(sock)
            resp['from_user'] = data[USER][ACCOUNT_NAME]
            resp['to_user'] = data['to_user']
            resp['text'] = data['text']
        except:
            print(f'Клиент {sock.fileno()} {sock.getpeername()} отключился')
            all_clients.remove(sock)
    return resp


def write_clients(requests, w_clients, all_clients, d_clients):
    # отправляем сообщение пользователю
    # перебираем словарь клиентов {сокет: имя}
    for c_socket, c_name in d_clients.items():
        # если в принятом сообщении имя получателя есть в словаре
        # и сокет есть в списке принимающих сокетов
        if requests['to_user'] == c_name and c_socket in w_clients:
            send_message(c_socket, requests)
        # если имя получателя не указано
        elif not requests['to_user']:
            # отправим сообщение всем
            send_message(c_socket, requests)


def main():
    try:
        port = int(sys.argv[sys.argv.index('-p') + 1]
                   ) if '-p' in sys.argv else DEFAULT_PORT
        if not 1024 < port < 65535:
            raise ValueError
    except:
        log.warning(
            'Номер порта должен быть числом в пределах от 1024 до 65535.')
        sys.exit(1)
    ip = sys.argv[sys.argv.index('-a') + 1] if '-a' in sys.argv else ''

    stream = socket(AF_INET, SOCK_STREAM)
    stream.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    stream.bind((ip, port))
    stream.listen(MAX_CONNECTIONS)
    print('proslushka')
    stream.settimeout(0.2)
    log.info(f'Запущен сервер: ip {ip}, port {port}')

    clients = []
    d_clients = {}
    while True:
        try:
            client, addr = stream.accept()
            client_name = get_message(client)[USER][ACCOUNT_NAME]
        except OSError:
            pass
        else:
            log.info(f'Получен запрос на соединение от {addr}')
            print(f'Получен запрос на соединение от {addr}')
            clients.append(client)
            # d_clients[client_name] = client
            # print(f'Клиенты онлайн: {set(d_clients.keys())}')
            d_clients[client] = client_name
            print(f'Клиенты онлайн: {set(d_clients.values())}')
        finally:
            r_clients = []
            w_clients = []
            try:
                r_clients, w_clients, e = select.select(clients, clients, [])
            except:
                pass
            requests = read_clients(r_clients, clients)

            if requests:
                write_clients(requests, clients, clients, d_clients)
 

if __name__ == '__main__':
    print('Сервер запущен')
    main()
