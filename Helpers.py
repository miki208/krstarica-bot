import sys

def getName(data):
	return data.split('!',1)[0][1:]
	
def prepare_data(data):
	return data.strip().split(' ')

def print_unicode(data):
	sys.stdout.buffer.write((data + '\n').encode('utf-8'))
	sys.stdout.flush()
