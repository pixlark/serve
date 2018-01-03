#!/usr/bin/python3

import socket as sk
import threading as th
import configparser as cr
import select as sl
import sys
import time

if len(sys.argv) < 2:
	print('Provide a username please')
	quit()

config = cr.ConfigParser()
config.read('cfg')

ip = config['client']['chat_server']
port = int(config['client']['port'])

sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
sock.connect((ip, port))
sock.send(b'JOIN' + sys.argv[1].encode())

running = True

def send_loop():
	global running
	while running:
		msg = input('')
		if msg.lower() == 'quit' or msg.lower() == 'q':
			sock.send(b'QUIT')
			running = False
		sock.send(b'MESG' + msg.encode())

def listen_loop():
	global running
	while running:
		data = sock.recv(1024)
		if (data[:4] == b'MESG'):
			print(data[4:].decode())
		elif (data[:4] == b'DOWN'):
			print('The server has shut down')
			running = False
		elif (data[:4] == b'QUIT'):
			print('{} has quit'.format(data[4:].decode()))
		elif (data[:4] == b'JOIN'):
			print('{} has joined'.format(data[4:].decode()))

listen_thread = th.Thread(target=listen_loop, daemon=True)
send_thread   = th.Thread(target=send_loop, daemon=True)

listen_thread.start()
send_thread.start()

while running:
	pass

sock.close()
