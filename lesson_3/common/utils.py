import json, logging, logs.client_log_config, logs.server_log_config
from .variables import ENCODING, MAX_LENGHT_MESSAGE


def send_message(socket, message):
    '''
    на вход передаётся сокет и сообщение в виде словаря
    функция кодирует и отправляет сообщение
    '''

    if not isinstance(message, dict):
        raise TypeError
    message = json.dumps(message).encode(ENCODING)
    socket.send(message)

def get_message(client):
    '''
    функция принимает и декодирует сообщение
    возвращает словарь
    '''
    encoded_response = client.recv(MAX_LENGHT_MESSAGE)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        if isinstance(json_response, str):
            response = json.loads(json_response)
            if isinstance(response, dict):
                return response
            raise ValueError
        raise ValueError
    raise ValueError


