#!/usr/bin/python3

import errno
import socket as sk
import threading as th
import time

sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
sock.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', 5005))
sock.listen(5)

clients = []
threads = []

clients.append(sock.accept())
print('First client connected from', clients[0][1])
clients.append(sock.accept())
print('Second client connected from', clients[1][1])

def manage_client(client, addr):
	print('Listening to messages from', addr)
	while True:
		data = client.recv(1024)
		print('HEADER', data[:4])
		if (data[:4] == b'MESG'):
			print(str(addr) + ':', data[4:])
			for c in clients:
				if (c[1] == addr):
					continue
				c[0].send(data[4:])
		elif (data[:4] == b'QUIT'):
			print(str(addr), 'has quit the conversation')
			return

for c in clients:
	threads.append(th.Thread(target=manage_client, args=c))
	threads[-1].start()

for t in threads:
	t.join()
	
for c in clients:
	c[0].close()

