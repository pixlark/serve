#!/usr/bin/python3

import socket as sk
import threading as th
import configparser as cr
import select as sl
import sys
import time
import queue
import tkinter as tk
import enum
import json

running = True
sock    = None

eventq = queue.Queue()

class Event():
	def __init__(self, etype, data):
		self.etype = etype
		self.data  = data

class EventType(enum.Enum):
	MESSAGE = 0
	DOWN    = 1
	QUIT    = 2
	JOIN    = 3
	LIST    = 4

def send_loop():
	global running
	while running:
		msg = input('')
		if msg.lower() == 'quit' or msg.lower() == 'q':
			running = False
		sock.send(b'MESG' + msg.encode())
	sock.send(b'QUIT')

def send_message(msg):
	sock.send(b'MESG' + msg.encode())

def listen_loop():
	global running
	while running:
		try:
			data = sock.recv(1024)
		except sk.timeout:
			continue
		data = data.strip(b'\0')
		requests = data.split(b'\0')
		for req in requests:
			if (req[:4] == b'MESG'):
				eventq.put(Event(EventType.MESSAGE, req[4:].decode()))
				print(req[4:].decode())
			elif (req[:4] == b'DOWN'):
				eventq.put(Event(EventType.DOWN, None))
				print('The server has shut down')
			elif (req[:4] == b'QUIT'):
				eventq.put(Event(EventType.QUIT, req[4:].decode()))
				print('{} has quit'.format(req[4:].decode()))
				running = False # TODO(pixlark): Move this to gui_loop?
			elif (req[:4] == b'JOIN'):
				eventq.put(Event(EventType.JOIN, req[4:].decode()))
				print('{} has joined'.format(req[4:].decode()))
			elif (req[:4] == b'LIST'):
				eventq.put(Event(EventType.LIST, req[4:].decode()))

def gui_loop(widgets):
	global eventq
	global running
	while running:
		try:
			event = eventq.get(False)
		except queue.Empty:
			time.sleep(0.1);
			continue
		print(event.etype)
		if   event.etype == EventType.MESSAGE:
			seperator = event.data.find(':')
			username = event.data[:seperator]
			message  = event.data[seperator+1:]
			widgets['messages']['state'] = tk.NORMAL
			widgets['messages'].insert(tk.END, '{0}: {1}\n'.format(username, message))
			widgets['messages']['state'] = tk.DISABLED
			widgets['messages'].see(tk.END)
		elif event.etype == EventType.JOIN:
			widgets['connected'].insert(tk.END, event.data)
		elif event.etype == EventType.LIST:
			clients = json.loads(event.data)
			if len(clients) > 0:
				widgets['connected'].insert(tk.END, clients)
			
			
def setup_root(root, username):
	widgets = {}
	
	widgets['messages'] = tk.Text(root, state=tk.DISABLED)
	widgets['messages'].grid(row=0, column=0, columnspan=2, padx=(6, 3), pady=(6, 3), stick=tk.W)
	
	widgets['entry_box'] = tk.Text(root, height=2)
	widgets['entry_box'].grid(row=1, column=0, stick=tk.W+tk.E, padx=(6, 3), pady=(3, 6))

	widgets['connected'] = tk.Listbox(root);
	widgets['connected'].grid(row=0, column=1, padx=(3, 6), pady=(6, 3), stick=tk.E+tk.N+tk.S)

	def send_from_box():
		message = widgets['entry_box'].get('1.0', tk.END)
		message = message.strip('\n')
		widgets['entry_box'].delete('1.0', tk.END)
		send_message(message)
		eventq.put(Event(EventType.MESSAGE, "{0}:{1}".format(username, message)))
	
	widgets['send_button'] = tk.Button(root, text="Send", command=send_from_box)
	widgets['send_button'].grid(row=1, column=1, padx=(3, 6), pady=(3, 6), stick=tk.N+tk.S+tk.E+tk.W)
	#widgets['send_button'].pack(in_=widgets['entry_frame'], side=tk.LEFT)
	root.bind("<Return>", lambda event: widgets['send_button'].invoke())
	
	return widgets

def main():
	global running
	global sock
	if len(sys.argv) < 2:
		print('Provide a username please')
		quit()

	config = cr.ConfigParser()
	config.read('cfg')

	ip = config['client']['chat_server']
	port = int(config['client']['port'])

	sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
	sock.settimeout(1)
	sock.connect((ip, port))
	sock.send(b'JOIN' + sys.argv[1].encode())

	listen_thread = th.Thread(target=listen_loop, daemon=True)
	listen_thread.start()

	root = tk.Tk()
	root.title("Chat program")
	widgets = setup_root(root, sys.argv[1])

	gui_thread = th.Thread(target=gui_loop, args=(widgets,), daemon=True)
	gui_thread.start()
	
	root.mainloop()
	
	running = False
	listen_thread.join()
	gui_thread.join()

	sock.send(b'QUIT')

	sock.close()

if __name__ == "__main__":
	main()
