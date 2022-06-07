from subprocess import Popen, CREATE_NEW_CONSOLE
from time import sleep

p_list = [] 

while True:
    print('Для закрытия всех клиентов нажмите "x"')
    print('Для выхода из программы нажмите "q"')

    val = input('Сколько клиентов хотите запустить?: ')
    if val == 'q':
        break
    elif val.isdigit():
        p_list.append(Popen('python server.py', creationflags=CREATE_NEW_CONSOLE))
        # for i in range(int(val)):
        #     print(f'Запуск клиент {i+1}')
        #     p_list.append(Popen('python client.py', creationflags=CREATE_NEW_CONSOLE))
        # print(f'Запущено {val} клиентов')
    elif val == 'x':
        for p in p_list:
            p.kill()
        p_list.clear()

# import subprocess

# PROCESS = []

# while True:
#     ACTION = input('Выберите действие: q - выход, '
#                    's - запустить сервер и клиенты, x - закрыть все окна: ')

#     if ACTION == 'q':
#         break
#     elif ACTION == 's':
#         PROCESS.append(subprocess.Popen('python server.py',
#                                         creationflags=subprocess.CREATE_NEW_CONSOLE))
#         for i in range(2):
#             PROCESS.append(subprocess.Popen('python client.py -m send',
#                                             creationflags=subprocess.CREATE_NEW_CONSOLE))
#         for i in range(5):
#             PROCESS.append(subprocess.Popen('python client.py -m listen',
#                                             creationflags=subprocess.CREATE_NEW_CONSOLE))
#     elif ACTION == 'x':
#         while PROCESS:
#             VICTIM = PROCESS.pop()
#             VICTIM.kill()