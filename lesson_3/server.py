import sys, logging, logs.server_log_config
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



def main():
    try:
        port = int(sys.argv[sys.argv.index('-p') + 1]) if '-p' in sys.argv else DEFAULT_PORT
        if not 1024 < port < 65535:
            raise ValueError
    except:
        log.warning('Номер порта должен быть числом в пределах от 1024 до 65535.')
        sys.exit(1)
    ip = sys.argv[sys.argv.index('-a') + 1] if '-a' in sys.argv else DEFAULT_IP

    stream = socket(AF_INET, SOCK_STREAM)
    stream.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    stream.bind((ip, port))
    stream.listen(MAX_CONNECTIONS)
    log.info(f'Запущен сервер: ip {ip}, port {port}')



    while True:
        client, addr = stream.accept()
        try:
            message_from_client = get_message(client)
            response = response_message(message_from_client)
            send_message(client, response)
            client.close()
        except:
            log.warning('Принято некорректное сообщение от клиента')
            client.close()

if __name__ == '__main__':
    main()