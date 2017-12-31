#!/usr/bin/python3

import socket as sk

ip = '127.0.0.1'
port = 5005
buffer_size = 1024

sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
sock.connect((ip, port))
sock.send(message.encode())
response = sock.recv(buffer_size)
print('Received response: ', response)
sock.close()
