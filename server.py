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

def manage_client(client, addr):
	#print('Listening to messages from', addr)
	while running:
		if (len(sl.select([client], [], [])[0]) > 0):
			data = client.recv(1024)
		else:
			time.sleep(1)
			continue
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

def listen_for_new_clients():
	while running:
		try:
			clients.append(sock.accept())
		except sk.timeout:
			continue
		print(clients[-1][1], 'has joined the conversation')
		threads.append(th.Thread(target=manage_client, args=clients[-1]))
		threads[-1].start()

listen_thread = th.Thread(target=listen_for_new_clients)
listen_thread.start()

while True:
	i = input('')
	if (i.lower() == 'quit' or i.lower() == 'q'):
		print('Shutting down...')
		running = False
		for c in clients:
			c[0].send('DOWN'.encode())
		break
	
for c in clients:
	c[0].close()

