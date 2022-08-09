from subprocess import Popen, CREATE_NEW_CONSOLE
from time import sleep
import os

p_list = []

while True:
    print('Для закрытия всех клиентов нажмите "x"')
    print('Для выхода из программы нажмите "q"')

    val = input('Сколько клиентов хотите запустить?: ')
    if val == 'q':
        break
    elif val.isdigit():
        p_list.append(Popen(['python', os.path.abspath(os.path.join(
            'lesson_3', 'server.py'))], creationflags=CREATE_NEW_CONSOLE))
        for i in range(int(val)):

            print(f'Запуск клиент {i+1}')
            p_list.append(Popen(['python', os.path.abspath(os.path.join(
                'lesson_3', 'client.py')), '-u', f'{i+1}'], creationflags=CREATE_NEW_CONSOLE))
        print(f'Запущено {val} клиентов')
    elif val == 'x':
        for p in p_list:
            p.kill()
        p_list.clear()
