from ast import While
import sys, time, socket, logging, logs.client_log_config
from common.variables import *
from common.utils import send_message, get_message

log = logging.getLogger('app.client')

def create_message(account_name='guest'):
    return {
        ACTION: PRESENCE,
        TIME: time.strftime('%d.%m.%Y %H:%M:%S', time.localtime()),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    
def main():
    try:
        port = int(sys.argv[sys.argv.index('-p') + 1]) if '-p' in sys.argv else DEFAULT_PORT
        if not 1024 < port < 65535:
            raise ValueError
    except:
        log.warning('Введён некорректный порт. Клиент не запущен')
        sys.exit(1)
    ip = sys.argv[sys.argv.index('-a') + 1] if '-a' in sys.argv else DEFAULT_IP

    if 'send' not in sys.argv: # client-listener
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
            log.info(f'Клиент запущен с ip {ip}, port {port}')
            stream.connect((ip, port))
            while True:
                resp = stream.recv(MAX_LENGHT_MESSAGE).decode(ENCODING)
                print(resp)
                if resp == 'exit':
                    break

    else: #client-sender
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
            log.info(f'Клиент запущен с ip {ip}, port {port}')
            stream.connect((ip, port))
            while True:
                message = input('Введите сообщение: ')
                if message == 'exit':
                    stream.send(message.encode(ENCODING))
                    break
                stream.send(message.encode(ENCODING))


if __name__ == '__main__':
    main()
