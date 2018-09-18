from Helpers import getName

class AbstractCommandHandler:
	def __init__(self, context):
		self.context = context
		
	def filter(self):
		return True
		
	def run(self, command):
		self.command = command
		
		if self.filter():
			self.behaviour()
			return True
		return False
			
	def behaviour(self):
		pass
		
class AbstractExitHandler(AbstractCommandHandler):
	def __init__(self, context):
		super(AbstractExitHandler, self).__init__(context)
		
	def filter(self):
		return super(AbstractExitHandler, self).filter() and self.command[0] == 'ERROR'
		
	def behaviour(self):
		exit()
		
class AbstractEndOfNamesHandler(AbstractCommandHandler):
	def __init__(self, context):
		super(AbstractEndOfNamesHandler, self).__init__(context)
		
	def filter(self):
		return super(AbstractEndOfNamesHandler, self).filter() and self.command[1] == '366' and self.command[2] == self.context.botNick and\
			self.command[3] == self.context.channel
		
	def behaviour(self):
		pass
		
class AbstractNamReplyHandler(AbstractCommandHandler):
	def __init__(self, context):
		super(AbstractNamReplyHandler, self).__init__(context)
		
	def filter(self):
		return super(AbstractNamReplyHandler, self).filter() and self.command[1] == '353' and self.command[2] == self.context.botNick and\
			self.command[4] == self.context.channel
		
	def behaviour(self):
		pass
		
class AbstractOnUserJoinHandler(AbstractCommandHandler):
	def __init__(self, context):
		super(AbstractOnUserJoinHandler, self).__init__(context)
		
	def filter(self):
		return super(AbstractOnUserJoinHandler, self).filter() and self.command[1] == 'JOIN' and self.command[2][1:] == self.context.channel
		
	def behaviour(self):
		pass
		
class AbstractOnUserLeaveHandler(AbstractCommandHandler):
	def __init__(self, context):
		super(AbstractOnUserLeaveHandler, self).__init__(context)
		
	def filter(self):
		return super(AbstractOnUserLeaveHandler, self).filter() and (\
				(self.command[1] == 'PART' and self.command[2] == self.context.channel)\
			or\
				(self.command[1] == 'QUIT')\
			)
		
	def behaviour(self):
		pass
		
class ReadyToJoinHandler(AbstractCommandHandler):
	def __init__(self, context):
		super(ReadyToJoinHandler, self).__init__(context)
		
	def filter(self):
		return super(ReadyToJoinHandler, self).filter() and self.command[0] == ':irc.krstarica.com' and self.command[1] == 'NOTICE' and\
			self.command[2] == self.context.botNick and ' '.join(self.command[3:]).startswith(':Pristup Vam je dozvoljen!')
			
	def behaviour(self):
		self.context.send_data("JOIN " + self.context.channel + "\n")
		
class EndOfMOTDHandler(AbstractCommandHandler):
	def __init__(self, context):
		super(EndOfMOTDHandler, self).__init__(context)

	def filter(self):
		return super(EndOfMOTDHandler, self).filter() and (self.command[1] == '376' or self.command[1] == '422')
		
	def behaviour(self):
		self.context.send_data("NS IDENTIFY " + self.context.botPassword + "\n")
		
class PingHandler(AbstractCommandHandler):
	def __init__(self, context):
		super(PingHandler, self).__init__(context)
	
	def filter(self):
		return super(PingHandler, self).filter() and self.command[0] == 'PING'
		
	def behaviour(self):
		self.context.send_data("PONG " + self.command[1] + "\n")
		
class AbstractMessageHandler(AbstractCommandHandler):
	def __init__(self, context):
		super(AbstractMessageHandler, self).__init__(context)
		
	def filter(self):
		return super(AbstractMessageHandler, self).filter() and len(self.command) >= 2 and self.command[1] == 'PRIVMSG'

class AdminMessageHandler(AbstractMessageHandler):
	def __init__(self, context):
		super(AdminMessageHandler, self).__init__(context)
		
	def filter(self):
		return super(AdminMessageHandler, self).filter() and getName(self.command[0]) == self.context.adminNick and self.command[2] == self.context.botNick
		
	def behaviour(self):
		if ' '.join(self.command[3:]) == ':QUIT':
			self.context.send_msg("04,15Igrica je zaustavljena!")
			self.context.send_data("QUIT Goodbye!\n")
			