'''Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе. Важно: решение должно быть универсальным, т.е. не зависеть от того, какие конкретно слова мы исследуем.
'''

from task_2 import byte_type


def check_bytes(word):
    try:
        byte_type(word)
        print(f'Слово "{word}" возможно записать в байтовом типе')

    except SyntaxError as e:
        if e.args[0] == 'bytes can only contain ASCII literal characters.':
            print(f'Слово "{word}" НЕ возможно записать в байтовом типе')
        else:
            print('Неизвестная ошибка')
        
words = ['attribute', 'класс', 'функция', 'type']

for word in words:
    check_bytes(word)
