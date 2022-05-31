import sys
import traceback
import logging


# l = logging.getLogger('test')
# l.setLevel(logging.DEBUG)
# log_hand = logging.StreamHandler()
# log_form = logging.Formatter('%(asctime)s %(levelname)-9s %(filename)-15s %(message)s')
# log_hand.setFormatter(log_form)
# log_hand.setLevel(logging.DEBUG)
# l.addHandler(log_hand)

# def log(loger):
#     def wrapper(loger):
#         names_funcions = []
#         for i in traceback.extract_stack()[:-1]:
#             names_funcions.append(list(i)[-1])
#         f = func()
#         loger.info(f'{func} была вызвана {names_funcions}')
#     return wrapper

# def loger(loger):
#     def deco(func):
#         def wrapper(*args, **kwargs):
#             names_funcions = []        
#             for i in traceback.extract_stack()[:-1]:
#                 names_funcions.append(list(i)[-1])
#             loger.info(f'запуск функции {names_funcions}')
#             f = func(*args, **kwargs)
#             return f
#         return wrapper
#     return deco

def log(func):
    def wrapper(*args, **kwargs):
        log_name = 'app.server' if sys.argv[0].endswith('server.py') else 'app.client'
        LOGGER = logging.getLogger(log_name)
        f = func(*args, **kwargs)
        cal_func = traceback.format_stack()[0].strip().split()[-1]
        LOGGER.info(f'Функция {func.__name__} вызвана из функции {cal_func}')
        return f
    return wrapper


@log
def func(x):
    # print(traceback.format_stack()[0].strip().split()[-1])
    return x*x


def func_2(x):
    
    return func(x)


if __name__ == '__main__':

    # print(func.__name__)
    # print(func.__module__)
    # print(traceback.format_stack())
    func_2(2)