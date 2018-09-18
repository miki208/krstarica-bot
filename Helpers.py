import socket
import sys
import threading

class Context:
	def __init__(self, server, port, channel, botNick, botPassword, adminNick, DEBUG = True):
		self.server = server
		self.port = port
		self.channel = channel
		self.botNick = botNick
		self.botPassword = botPassword
		self.adminNick = adminNick
		
		self.__lock = threading.RLock()
		
		self.buffer = ""
		self.DEBUG = DEBUG

		self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ircsock.connect((self.server, self.port))

	def send_data(self, data):
		if self.DEBUG:
			print_unicode("DEBUG-SEND: " + data)
	
		self.ircsock.send(bytes(data, "UTF-8"))

	def send_msg(self, msg):
		self.send_data("PRIVMSG " + self.channel + " :" + msg + "\n")
		
	def send_notice(self, user, msg):
		self.send_data("NOTICE " + user + " :" + msg + "\n")

	def recv_data(self):
		with self.__lock:
			data = self.ircsock.recv(2048).decode("UTF-8", errors = 'replace')
		return data
		
	def get_next_line(self):
		while self.buffer.find("\n") == -1:
			self.buffer = self.buffer + self.recv_data()
	
		temp = self.buffer.split("\n", 1)
		if len(temp) == 1:
			self.buffer = ""
		else:
			self.buffer = temp[1]

		if self.DEBUG:
			print_unicode("DEBUG-RECV: " + temp[0])

		return temp[0]
		
	def connect(self):
		self.send_data("USER " + self.botNick + " " + self.botNick + " " + self.botNick + " " + self.botNick + "\n")
		self.send_data("NICK " + self.botNick + "\n")

def getName(data):
	return data.split('!',1)[0][1:]
	
def prepare_data(data):
	return data.strip().split(' ')

def print_unicode(data):
	sys.stdout.buffer.write((data + '\n').encode('utf-8'))
	sys.stdout.flush()