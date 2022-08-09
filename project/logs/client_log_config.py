import logging, sys, os

os.chdir(sys.path[0])



# создаём объект логер
log = logging.getLogger('app.client')
# создаём стрим хендлер
# stream_handler = logging.StreamHandler(sys.stderr)
# stream_handler.setLevel(logging.DEBUG)
# создаём файловый хендлер
file_handler = logging.FileHandler('logs/client.log', encoding='utf-8')
# создаём форматтер

formatter = logging.Formatter("%(asctime)s %(levelname)-10s %(filename)-20s %(message)s")
# к хендлерам добавляем форматтер
# stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# log.addHandler(stream_handler)
log.addHandler(file_handler)

log.setLevel(logging.DEBUG)


if __name__ == '__main__':


    log.debug('debug')
    log.info('info')
    log.warning('warning')
    # log.error('error')
    # log.critical('critical')