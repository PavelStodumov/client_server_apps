import sys, time, socket
from common.variables import *
from common.utils import send_message, get_message
    

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
        print('Номер порта должен быть числом в пределах от 1024 до 65535.')
        sys.exit(1)
    ip = sys.argv[sys.argv.index('-a') + 1] if '-a' in sys.argv else DEFAULT_IP

    stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stream.connect((ip, port))
    message_to_server = create_message()
    send_message(stream, message_to_server)

    response = get_message(stream)
    print(response)


if __name__ == '__main__':
    main()