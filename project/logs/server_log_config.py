import logging, os, sys
from logging.handlers import TimedRotatingFileHandler

os.chdir(sys.path[0])

log = logging.getLogger('app.server')

# file_handler = logging.FileHandler('logs/server.log', encoding='utf-8')
file_handler = TimedRotatingFileHandler('logs/server.log', 
                                        when='h', 
                                        interval=24, 
                                        backupCount=2,  
                                        encoding='utf-8')

file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)-10s %(filename)-20s %(message)s")
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    log.warning('warning')


