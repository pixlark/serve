#!/usr/bin/python3

import socket as sk
import threading as th

ip = '127.0.0.1'
port = 5006
buffer_size = 1024

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
