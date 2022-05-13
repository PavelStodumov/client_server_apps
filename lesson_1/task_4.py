'''Преобразовать слова «разработка», «администрирование», «protocol», «standard» из
строкового представления в байтовое и выполнить обратное преобразование (используя
методы encode и decode).
'''

def show_list(lst):
    for i in lst:
        print(i)


words = ['разработка', 'администрирование', 'protocol', 'standard']
byte_words = list(map(lambda w: w.encode('utf-8'), words))

show_list(byte_words)

decode_words = list(map(lambda w: w.decode('utf-8'), byte_words))

show_list(decode_words)