#!/usr/bin/python3

import errno
import socket as sk
import threading as th
import time
import configparser as cr
import select as sl
import json

sock = None
clients = []
threads = []
running = True

class Client:
	def __init__(self, tup, username="undeclared"):
		self.connection = tup[0]
		self.address = tup[1]
		self.username = username

def data_in_socket(socket):
	return len(sl.select([socket], [], [])) > 0
		
def manage_client(client):
	global clients
	while True:
		if data_in_socket(client.connection):
			data = client.connection.recv(1024)
		else:
			time.sleep(1)
			continue
		print("{0} : ".format(data[:4]), end='')
		if   data[:4] == b'MESG':
			print(client.username.decode() + ':', data[4:].decode())
			for c in clients:
				if c.address == client.address:
					continue
				c.connection.send(b'\0' + b'MESG' + client.username + b':' + data[4:])
				print('Forwarded to', c.username.decode())
		elif data[:4] == b'QUIT':
			print(client.username.decode(), 'has quit')
			clients = [c for c in clients if c.address != client.address]
			return

def listen_for_new_clients():
	global clients
	while running:
		try:
			client = Client(sock.accept())
		except sk.timeout:
			continue
		client.username = client.connection.recv(1024)[4:]
		print(client.username, 'has joined')
		print(json.dumps([c.username.decode() for c in clients]))
		client.connection.send(b'LIST' +
							   json.dumps([c.username.decode() for c in clients])
							   .encode())
		clients.append(client)
		for c in clients:
			c.connection.send(b'\0' + b'JOIN' + client.username)
		threads.append(th.Thread(target=manage_client, args=(client,), daemon=True))
		threads[-1].start()

def main():
	global sock
	global clients
	global running

	# Load configuration
	config = cr.ConfigParser()
	config.read('cfg')
	port = int(config['server']['port'])
	print('Loaded configuration')

	# Start listening
	sk.setdefaulttimeout(float(config['server']['timeout']))
	print('Timeout set to', config['server']['timeout'])

	sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
	sock.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
	sock.bind(('0.0.0.0', port))
	sock.listen(5)
	print('Listening on port', port)

	listen_thread = th.Thread(target=listen_for_new_clients)
	listen_thread.start()

	# Wait for commands
	while True:
		i = input('')
		if i.lower() == 'quit' or i.lower() == 'q':
			print('Shutting down...')
			running = False
			for c in clients:
				c[0].send(b'\0' + b'DOWN')
			break
	
	for c in clients:
		c[0].close()
	
if __name__ == "__main__":
	main()
