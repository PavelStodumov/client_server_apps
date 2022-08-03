
from base64 import encode
from cgi import test
from http import server
import json, sys, unittest, os
from socket import *


sys.path.insert(0, os.path.join(sys.path[0], '..'))

from common.utils import send_message, get_message
from common.variables import ENCODING, DEFAULT_IP, DEFAULT_PORT, MAX_CONNECTIONS, MAX_LENGHT_MESSAGE



class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message):
        encoded_message = json.dumps(self.test_dict)
        self.encoded_message = encoded_message.encode(ENCODING)
        self.received_message = message

    def recv(self, max_lengh):
        json_message = json.dumps(self.test_dict)
        return json_message.encode(ENCODING)



class UtilsTest(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_message = {'status': 'ok', 'response': 200}
        self.test_socket = TestSocket(self.test_message)

    def test_send_message_dict(self):
        # отправляем сообщение на сокет в виде словаря
        send_message(self.test_socket, self.test_message)
        # принятое сообщение ожидаем в виде json строки, в кодировке ENCODING
        self.assertEqual(self.test_socket.received_message, json.dumps(self.test_message).encode(ENCODING))

    def test_send_message_no_dict(self):
        # отправляем сообщение на сокет в виде строки
        # ожидаем ошибку TypeError
        self.assertRaises(TypeError, send_message, self.test_socket, 'Hello')

    def test_get_message_dict(self):
        # принимаем сообщение, получаем ответ dict
        self.assertEqual(get_message(self.test_socket), self.test_socket.test_dict)

    def test_get_message_json(self):
        # преобразуем тестовое сообщение в json
        test_socket = TestSocket(json.dumps(self.test_socket.test_dict))
        # ожидаем ошибку ValueError. функция должна принимать байты
        self.assertRaises(ValueError, get_message, test_socket)
        
    

if __name__ == '__main__':
    unittest.main()