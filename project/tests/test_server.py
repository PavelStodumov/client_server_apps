import sys, os, unittest, socket
from urllib import response

sys.path.insert(0, os.path.join(sys.path[0], '..'))

from common.variables import PRESENCE, RESPONSE
import server


class TestServer(unittest.TestCase):
    def setUp(self) -> None:
        self.test_ok_message = {
            'action': PRESENCE,
            'user': {
                'account_name': 'guest'
            }
        }
        self.test_bad_message = {
            'action': None,
            'user': {
                'account_name': None
            }
        }
        self.ok_response = {
            RESPONSE: '200',
            'status': 'ok'
            }
        self.bad_response = {
            RESPONSE: '400',
            'status': 'Bad request'
        }

    def test_response_message_ok(self):
        # корректное сообщение
        response = server.response_message(self.test_ok_message)
        # ожидаем ответ
        self.assertEqual(response, self.ok_response)

    def test_response_message_bad(self):
        # сообщение с неуказанным действием и юзером
        response = server.response_message(self.test_bad_message)
        # ожидаем ответ bad request
        self.assertEqual(response, self.bad_response)

    def test_response_message_no_data(self):
        # сообщение с пустым словарём не обрабатывается
        self.assertRaises(KeyError, server.response_message, {})

    def test_response_message_no_dict(self):
        # сообщение с типом данных, отличных от dict вызывает TypeError
        self.assertRaises(TypeError, server.response_message, 'Hello')
    


if __name__ == '__main__':
    unittest.main()
