#!/usr/bin/python3

import socket as sk
import threading as th
import configparser as cr
import select as sl
import sys
import time

config = cr.ConfigParser()
config.read('cfg')

ip = config['client']['chat_server']
port = int(config['client']['port'])

sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
sock.connect((ip, port))

running = True

def send_loop():
	while True:
		msg = input('> ')
		if msg.lower() == 'quit' or msg.lower() == 'q':
			sock.send(b'QUIT')
			break
		sock.send(b'MESG' + msg.encode())

def listen_loop():
	global running
	while True:
		if sl.select([sock], [], [])[0]:
			data = sock.recv(1024)
		else:
			time.sleep(0.05)
			continue
		if (data[:4] == b'MESG'):
			print(data[4:].decode() + '\n> ', end='')
		elif (data[:4] == b'DOWN'):
			print('The server has shut down.')
			return

listen_thread = th.Thread(target=listen_loop)
send_thread   = th.Thread(target=send_loop, daemon=True)

listen_thread.start()
send_thread.start()

listen_thread.join()

sock.close()
