'''Каждое из слов «class», «function», «method» записать в байтовом типе. Сделать это необходимо в автоматическом, а не ручном режиме, с помощью добавления литеры b к текстовому значению, (т.е. ни в коем случае не используя методы encode, decode или функцию bytes) и определить тип, содержимое и длину соответствующих переменных.
'''


def byte_type(word):
    return eval(f"b'{word}'")


if __name__ == '__main__':

    words = ['class', 'funtion', 'method']
    
    for word in words:
        word = byte_type(word)
        print(f'тип: {type(word)}', end=' ')
        print(f'содержимое: {word}', end=' ')
        print(f'длинна: {len(word)}')

