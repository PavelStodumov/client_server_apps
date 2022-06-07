import sys, logging, select
from socket import *
from common.variables import *
from common.utils import *

log = logging.getLogger('app.server')


def response_message(message):
    log.info(f'Принято сообщение: {message}')
    if message['action'] == PRESENCE and message['user']['account_name'] == 'guest':
        return {
            RESPONSE: '200',
            'status': 'ok'
            }
    return {
        RESPONSE: '400',
        'status': 'Bad request'
    }

def read_clients(r_clients, all_clients):
    resp = {}
    for sock in r_clients:
        try:
            data = sock.recv(1024).decode('utf-8')
            resp[sock] = data
        except:
            print(f'Клиент {sock.fileno()} {sock.getpeername()} отключился')
            all_clients.remove(sock)
    return resp

def write_clients(requests, w_clients, all_clients):
    for sock in w_clients:
        for value in requests.values():
            sock.send(f'{value}'.encode(ENCODING))


def main():
    try:
        port = int(sys.argv[sys.argv.index('-p') + 1]) if '-p' in sys.argv else DEFAULT_PORT
        if not 1024 < port < 65535:
            raise ValueError
    except:
        log.warning('Номер порта должен быть числом в пределах от 1024 до 65535.')
        sys.exit(1)
    ip = sys.argv[sys.argv.index('-a') + 1] if '-a' in sys.argv else ''

    stream = socket(AF_INET, SOCK_STREAM)
    stream.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    stream.bind((ip, port))
    stream.listen(MAX_CONNECTIONS)
    stream.settimeout(0.2)
    log.info(f'Запущен сервер: ip {ip}, port {port}')

    clients = []
    while True:
        try:
            client, addr = stream.accept()
        except OSError:
            pass
        else:
            log.info(f'Получен запрос на соединение от {addr}')
            print(f'Получен запрос на соединение от {addr}')
            clients.append(client)
        finally:
            r_clients = []
            w_clients = []
            try:
                r_clients, w_clients, e = select.select(clients, clients, [])
            except:
                pass
            requests = read_clients(r_clients, clients)
            

            if requests:
                write_clients(requests, clients, clients)

            if 'exit' in requests.values():
                break

if __name__ == '__main__':
    print('Сервер запущен')
    main()
