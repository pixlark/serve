#!/usr/bin/python3

import errno
import socket as sk
import threading as th
import time

sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
sock.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
sock.bind(('127.0.0.1', 5005))
sock.listen(5)

quit()

clients = []

clients.append(sock.accept())
print('First client connected from', clients[0][1])
clients.append(sock.accept())
print('Second client connected from', clients[1][1])

def manage_client(client, addr):
	print('Listening to messages from', addr)
	while True:
		data = client.recv(1024)
		print(data)

for c in clients:
	client_thread = th.Thread(target=manage_client, args=c)
	client_thread.start()

for c in clients:
	c[0].close()

