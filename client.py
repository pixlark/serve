#!/usr/bin/python3

import socket as sk
import threading as th
import configparser as cr

config = cr.ConfigParser()
config.read('cfg')

ip = config['client']['chat_server']
port = int(config['client']['port'])

sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
sock.connect((ip, port))

def send_loop():
	while True:
		msg = input('> ')
		if (msg.lower() == 'quit' or msg.lower() == 'q'):
			sock.send(b'QUIT')
			break
		sock.send(b'MESG' + msg.encode())

def listen_loop():
	while True:
		data = sock.recv(1024)
		print(data.decode() + '\n> ', end='')

send_thread   = th.Thread(target=send_loop)
listen_thread = th.Thread(target=listen_loop, daemon=True)

send_thread.start()
listen_thread.start()

send_thread.join()

sock.close()
