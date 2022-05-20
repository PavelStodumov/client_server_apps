from socket import *

s = socket(AF_INET, SOCK_STREAM)
s.bind(('', 8888))
s.listen()

# while True:
for i in range(3):
    client, addr = s.accept()
    data = client.recv(1024).decode('utf-8')
    print(data)
    message = f'Ты написал {data}'
    client.send(message.encode('utf-8'))
    client.close()