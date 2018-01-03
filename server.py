#!/usr/bin/python3

import errno
import socket as sk
import threading as th
import time
import configparser as cr
import select as sl

config = cr.ConfigParser()
config.read('cfg')
port = int(config['server']['port'])
print('Loaded configuration')

sk.setdefaulttimeout(float(config['server']['timeout']))
print('Timeout set to', config['server']['timeout'])

sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
sock.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', port))
sock.listen(5)
print('Listening on port', port)

clients = []
threads = []

running = True

def manage_client(client, addr, username):
	while True:
		if len(sl.select([client], [], [])[0]) > 0:
			data = client.recv(1024)
		else:
			time.sleep(1)
			continue
		print('HEADER', data[:4])
		if data[:4] == b'MESG':
			print(username.decode() + ':', data[4:].decode())
			for c in clients:
				if c[1] == addr:
					continue
				c[0].send(data[:4] + username + b': ' + data[4:])
				print('Forwarded to', c[2].decode())
		elif data[:4] == b'QUIT':
			print(username.decode(), 'has quit')
			ri = -1
			for i in range(len(clients)):
				if clients[i][1] == addr:
					ri = i
				else:
					clients[i][0].send(b'QUIT' + username)
			if (ri == -1):
				raise RuntimeError('Something went wrong')
			del clients[ri]
			return

def listen_for_new_clients():
	while running:
		try:
			clients.append(sock.accept())
		except sk.timeout:
			continue
		username= clients[-1][0].recv(1024)[4:]
		clients[-1] = (clients[-1][0], clients[-1][1], username)
		print(clients[-1][2], 'has joined')
		for c in clients:
			c[0].send(b'JOIN' + username)
		threads.append(th.Thread(target=manage_client, args=clients[-1], daemon=True))
		threads[-1].start()

listen_thread = th.Thread(target=listen_for_new_clients)
listen_thread.start()

while True:
	i = input('')
	if i.lower() == 'quit' or i.lower() == 'q':
		print('Shutting down...')
		running = False
		for c in clients:
			c[0].send('DOWN'.encode())
		break
	
for c in clients:
	c[0].close()

