import sys, os, unittest

sys.path.insert(0, os.path.join(sys.path[0], '..'))

from client import create_message


class TestClientCreateMessage(unittest.TestCase):
    def test_create_message_no_args(self):
        # без аргументов
        message = create_message()
        # ожидаем словарь
        self.assertIs(type(message), dict)
        # с ключами 'action' и 'user'
        self.assertIn('action', message)
        self.assertIn('user', message)

    def test_create_message_with_arg(self):
        message = create_message('Hello')
        # ожидаем словарь, со значением 'account_name' = 'Hello'
        self.assertEqual(message['user']['account_name'], 'Hello')


if __name__ == '__main__':
    unittest.main()