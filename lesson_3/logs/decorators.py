import sys
import traceback
import logging


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