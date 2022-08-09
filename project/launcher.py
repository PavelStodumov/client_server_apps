import signal
from subprocess import Popen
import sys
import os
import platform
from time import sleep
if platform.system().lower() == 'windows':
    from subprocess import CREATE_NEW_CONSOLE



def launch_win():
    p_list = []
    while True:
        print('Для закрытия всех клиентов нажмите "x"')
        print('Для выхода из программы нажмите "q"')
        val = input('Сколько клиентов хотите запустить?: ')
        if val == 'q':
            break
        elif val.isdigit():
            p_list.append(Popen(['python', os.path.abspath(os.path.join(
                'project', 'server.py'))], creationflags=CREATE_NEW_CONSOLE))
            for i in range(int(val)):

                print(f'Запуск клиент {i+1}')
                p_list.append(Popen(['python', os.path.abspath(os.path.join(
                    'project', 'client.py')), '-u', f'{i+1}'], creationflags=CREATE_NEW_CONSOLE))
            print(f'Запущено {val} клиентов')
        elif val == 'x':
            for p in p_list:
                p.kill()
            p_list.clear()

def launch_un():
    p_list = []
    while True:
        print('Для закрытия всех клиентов нажмите "x"')
        print('Для выхода из программы нажмите "q"')

        val = input('Сколько клиентов хотите запустить?: ')
        if val == 'q':
            break
        elif val.isdigit():
            PYTHON_PATH = sys.executable
            BASE_PATH = os.path.dirname(os.path.abspath(__file__))
            server_full_path = f"{PYTHON_PATH} {BASE_PATH}/{'server.py'}"
            client_full_path = f"{PYTHON_PATH} {BASE_PATH}/{'client.py'}"

            args = ["gnome-terminal", "--disable-factory", "--", "bash", "-c"]

            p_list.append(Popen(args + [server_full_path], preexec_fn=os.setpgrp))
            for i in range(int(val)):
                sleep(0.2)
                print(f'Запуск клиент {i+1}')
                p_list.append(Popen(args + [client_full_path], preexec_fn=os.setpgrp))
            print(f'Запущено {val} клиентов')
        elif val == 'x':
            while p_list:
                victim = p_list.pop()
                os.killpg(victim.pid, signal.SIGINT)

if __name__ == '__main__':
    if platform.system().lower() == 'windows':
        launch_win()
    else:
        launch_un()
  