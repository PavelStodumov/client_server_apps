from chardet import detect

def get_encoding(file):
    with open(file, 'rb') as f:
        return f.detect()['encoding']

def get_data(*args):
    pass



# get_data('info_1.txt', 'info_2.txt', 'info_3.txt')
# get_encoding('info_1.txt')

with open('info_1.txt', 'rb') as f:
    print(f)