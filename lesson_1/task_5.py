'''Написать код, который выполняет пинг веб-ресурсов yandex.ru, youtube.com и преобразовывает результат из байтовового типа данных в строковый без ошибок для любой кодировки операционной системы.
'''


import subprocess
import platform
import chardet


HOSTS = ['yandex.ru', 'youtube.com']

def pinging(host, quantity):
    print('{:*^50}'.format(f'start pinging {host}'))
    os_param = '-n' if platform.system().lower() == 'windows' else '-c'
    ping_args = ['ping', os_param, str(quantity), host]
    ping = subprocess.Popen(ping_args, stdout=subprocess.PIPE)

    for line in ping.stdout:
        if line.isspace():
            continue
        coding = chardet.detect(line)['encoding']
        line.decode(coding).encode('utf-8')
        print('result:', line.decode('utf-8').strip())
    print('{:-^50}'.format(f'end pinging {host}'))


for host in HOSTS:
    pinging(host, 2)