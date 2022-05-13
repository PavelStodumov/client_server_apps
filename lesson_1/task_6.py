'''Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор». Далее забыть о том, что мы сами только что создали этот файл и исходить из того, что перед нами файл в неизвестной кодировке. Задача: открыть этот файл БЕЗ ОШИБОК вне зависимости от того, в какой кодировке он был создан.
'''
from chardet import detect

strings = ['сетевое программирование', 'сокет', 'декоратор']

with open('test_file.txt', 'w', encoding='utf-8') as f:
    for s in strings:
        f.write(s + '\n')

def get_encoding(file):
    with open(file, 'rb') as f:
        return detect(f.read())['encoding']
        
with open('test_file.txt', 'r', encoding=get_encoding('test_file.txt')) as f:
    content = f.read()
    print(content)

