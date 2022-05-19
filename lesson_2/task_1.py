from chardet import detect
import re
import csv
import os

# странное поведение: скрипт не видит файл без этого. рабочая директория client_server_apps
os.chdir('lesson_2') 



def get_encoding(file):
    with open(file, 'rb') as f:
        return detect(f.read())['encoding']

def get_data(*args):
    regex_prod = re.compile('Изготовитель системы:.+')
    regex_name = re.compile('Название ОС:.+')
    regex_code = re.compile('Код продукта:.+')
    regex_type = re.compile('Тип системы:.+')
    main_data = [['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']]
    os_prod_list, os_name_list, os_code_list, os_type_list = [], [], [], []
    for f in args:
        with open(f, 'r', encoding=get_encoding(f)) as file:
            content = file.read()
            os_prod_list.append(re.findall(regex_prod, content)[0].split(':')[1].strip())
            os_name_list.append(re.findall(regex_name, content)[0].split(':')[1].strip())
            os_code_list.append(re.findall(regex_code, content)[0].split(':')[1].strip())
            os_type_list.append(re.findall(regex_type, content)[0].split(':')[1].strip())
    for i in range(len(args)):
        main_data.append([os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]])
    return main_data

def write_to_csv(file, *args):
    with open(file, 'w', newline='') as f:
        f_writer = csv.writer(f)
        for row in get_data(*args):
            f_writer.writerow(row)

write_to_csv('info.csv', 'info_1.txt', 'info_2.txt', 'info_3.txt')


