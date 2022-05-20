from email import message
from socket import *

s = socket(AF_INET, SOCK_STREAM)
s.connect(('localhost', 8888))

message = input()
s.send(message.encode('utf-8'))
data = s.recv(1024)
print(data.decode('utf-8'))
