import dis
import sys
from pprint import pprint
sys.path.append('..')
from errors import ClientError, ServerError


class ServerVerifier(type):
    '''Метакласс для проверки сервера'''
    def __init__(cls, cls_name, cls_parrents, cls_attrs) -> None:
        
        # собираем все методы и атрибуты в список
        methods_and_attrs = []

        for attr in cls_attrs:
            try:
                instructions = dis.get_instructions(cls_attrs[attr])
            except:
                pass
            for i in instructions:

                # собираем все методы и атрибуты в список
                if i.opname == 'LOAD_GLOBAL' or i.opname == 'LOAD_METHOD' or i.opname == 'LOAD_ATTR':
                    methods_and_attrs.append(i.argval)

        # список не допустимых инструкций
        not_inst = ['connect']
        # список необходимых инструкций
        yes_inst = ['SOCK_STREAM', 'AF_INET']

        for i in not_inst:
            # Если в списке всех атрибутов и методов присутствует не допустимая инструкция
            # возбуждаем исключение
            if i in methods_and_attrs:
                ex_message = f'{i} не допустимо для сервера'
                raise ServerError(ex_message)

        for i in yes_inst:
            # Если в списке всех атрибутов и методов отсутствует необходимая инструкция
            # возбуждаем исключение
            if i not in methods_and_attrs:
                raise ServerError('non TCP')

            
        
class ClientVerifier(type):
    '''Метакласс для проверки клиента'''
    def __init__(cls, cls_name, cls_parrents, cls_attrs) -> None:
        
        # собираем все методы и атрибуты в список
        methods_and_attrs = []

        for attr in cls_attrs:
            try:
                instructions = dis.get_instructions(cls_attrs[attr])
            except:
                pass
            for i in instructions:

                # собираем все методы и атрибуты в список
                if i.opname == 'LOAD_GLOBAL' or i.opname == 'LOAD_METHOD' or i.opname == 'LOAD_ATTR':
                    methods_and_attrs.append(i.argval)

        # список не допустимых инструкций
        not_inst = ['accept', 'listen']
        # список необходимых инструкций
        yes_inst = ['sock']
        for i in not_inst:
            # Если в списке всех атрибутов и методов присутствует не допустимая инструкция
            # возбуждаем исключение
            if i in methods_and_attrs:
                ex_message = f'{i} не допустимо для клиента'
                raise ClientError(ex_message)

        for i in yes_inst:
            # Если в списке всех атрибутов и методов отсутствует необходимая инструкция
            # возбуждаем исключение
            if i not in methods_and_attrs:
                raise ClientError('non TCP')