from CommandHandler import *
from Quiz import Quiz
from Helpers import getName, print_unicode

def QueueHandlerFactory(factoryName, context):
	if factoryName == 'quiz':
		return QuizModeQueueHandler(context)
	else:
		raise ValueError('Unknown queue handler factory.')

class QuizModeQueueHandler:
	class TimeoutHandler(AbstractCommandHandler):
		def __init__(self, context, publicMessageHandler):
			super(QuizModeQueueHandler.TimeoutHandler, self).__init__(context)
			self.publicMessageHandler = publicMessageHandler
			
		def filter(self):
			return super(QuizModeQueueHandler.TimeoutHandler, self).filter() and getName(self.command[0]) == self.context.botNick and\
				self.command[1] == 'NOTICE' and self.command[2] == self.context.botNick and self.command[3] == ':TIMEOUT'
				
		def behaviour(self):
			self.context.send_msg("10,15Vreme je isteklo! Naša reč je bila 04" + self.publicMessageHandler.quiz.getWord() + '10.')
			text = self.publicMessageHandler.quiz.onRoundFinished()
			self.context.send_msg(text)
			
			if self.publicMessageHandler.quiz.getGamesPlayed() == 3:
				self.publicMessageHandler.quiz.setState(Quiz.GameState.GAME_FINISHED)
			else:
				self.publicMessageHandler.quiz.setState(Quiz.GameState.ROUND_FINISHED)

	class ExitHandler(AbstractExitHandler):
		def __init__(self, context, publicMessageHandler):
			super(QuizModeQueueHandler.ExitHandler, self).__init__(context)
			self.publicMessageHandler = publicMessageHandler
			
		def behaviour(self):
			self.publicMessageHandler.quiz.onClose() #first do all of the cleaning jobs (save data, stop timer...)
			super(QuizModeQueueHandler.ExitHandler, self).behaviour() #and then start closing procedure

	class OnUserLeaveHandler(AbstractOnUserLeaveHandler):
		def __init__(self, context, publicMessageHandler):
			super(QuizModeQueueHandler.OnUserLeaveHandler, self).__init__(context)
			self.publicMessageHandler = publicMessageHandler
			
		def behaviour(self):
			self.publicMessageHandler.quiz.onUserLeave(getName(self.command[0]))

	class OnUserJoinHandler(AbstractOnUserJoinHandler):
		def __init__(self, context, publicMessageHandler):
			super(QuizModeQueueHandler.OnUserJoinHandler, self).__init__(context)
			self.publicMessageHandler = publicMessageHandler
			
		def behaviour(self):
			name = getName(self.command[0])
			
			self.context.send_notice(name, "10,15Da biste videli pomoć, kucajte 04!help10.")
			self.publicMessageHandler.quiz.onUserJoin(name)

	class NamReplyHandler(AbstractNamReplyHandler):
		def __init__(self, context, publicMessageHandler):
			super(QuizModeQueueHandler.NamReplyHandler, self).__init__(context)
			self.publicMessageHandler = publicMessageHandler
			
		def behaviour(self):
			self.command[5] = self.command[5][1:]
			self.publicMessageHandler.quiz.setUsers([x if x[0] not in ['%', '@', '+'] else x[1:] for x in self.command[5:]])

	class EndOfNamesHandler(AbstractEndOfNamesHandler):
		def __init__(self, context, publicMessageHandler):
			super(QuizModeQueueHandler.EndOfNamesHandler, self).__init__(context)
			self.publicMessageHandler = publicMessageHandler
			
		def behaviour(self):
			self.publicMessageHandler.update() #deffered reaction to state change: it has to be called here, because room isn't ready before this event

	class PublicMessageHandler(AbstractMessageHandler):
		def __init__(self, context):
			super(QuizModeQueueHandler.PublicMessageHandler, self).__init__(context)
			self.quiz = Quiz(self)
		
		def filter(self):
			return super(QuizModeQueueHandler.PublicMessageHandler, self).filter() and self.command[2] == self.context.channel
		
		def behaviour(self):
			nick = getName(self.command[0])
			if self.command[3] == ':!o' or self.command[3] == ':!odgovor':
				if len(self.command) < 5:
					self.context.send_notice(nick, '04,15Niste naveli vaš odgovor.')
				self.quiz.checkAnswer(nick, ' '.join(self.command[4:]))
				
			elif len(self.command) == 4 and (self.command[3] == ':!z' or self.command[3] == ':!zadatak'):
				if self.quiz.getState() == Quiz.GameState.NEW_PUZZLE:
					self.context.send_notice(nick, self.quiz.getPuzzlePrint())
				else:
					self.context.send_notice(nick, "04,15Sačekajte sledeći zadatak.")
					
			elif len(self.command) == 4 and self.command[3] == ':!top5':
				self.context.send_notice(nick, self.quiz.getTop5Print())
				
			elif len(self.command) == 4 and self.command[3] == ':!kredit':
				self.context.send_notice(nick, "10,15Trenutno imate 04" + str(self.quiz.getCredit(nick)) + "10 kredita.")
				
			elif len(self.command) == 4 and self.command[3] == ':!help':
				for msg in self.quiz.getHelpPrint():
					self.context.send_notice(nick, msg)
			
		def update(self):
			state = self.quiz.getState()
			
			if state == Quiz.GameState.UNINITIALIZED:
				self.context.send_msg("10,15Učitavam ovu strava igricu...")
				self.quiz.loadGame()
			elif state == Quiz.GameState.INITIALIZED:
				self.context.send_msg("03,15Kviz je učitan. Uživajte!")
			elif state == Quiz.GameState.NOT_ENOUGH_PLAYERS:
				self.quiz.cancelTimer()
				self.context.send_msg("04,15Potrebna su bar dva igrača kako bih započeo igru.")
			elif state == Quiz.GameState.ENOUGH_PLAYERS:
				self.context.send_msg("03,15U redu, sada ima dovoljno igrača. Započinjem novu partiju.")
				self.quiz.startNewGame()
			elif state == Quiz.GameState.NEW_PUZZLE:
				self.context.send_msg(self.quiz.getPuzzlePrint())
			elif state == Quiz.GameState.TIMEOUT:
				self.context.send_notice(self.context.botNick, "TIMEOUT")
			elif state == Quiz.GameState.GAME_FINISHED:
				self.context.send_msg("10,15Partija je završena. Započinjem novu partiju...")
				self.quiz.startNewGame()
			elif state == Quiz.GameState.ROUND_FINISHED:
				self.quiz.startNewRound()

	class __QuizModeQueueHandler:
		def __init__(self, context):
			publicMessageHandler = QuizModeQueueHandler.PublicMessageHandler(context)
			endOfNamesHandler = QuizModeQueueHandler.EndOfNamesHandler(context, publicMessageHandler)
			namReplyHandler = QuizModeQueueHandler.NamReplyHandler(context, publicMessageHandler)
			onUserJoinHandler = QuizModeQueueHandler.OnUserJoinHandler(context, publicMessageHandler)
			onUserLeaveHandler = QuizModeQueueHandler.OnUserLeaveHandler(context, publicMessageHandler)
			exitHandler = QuizModeQueueHandler.ExitHandler(context, publicMessageHandler)
			timeoutHandler = QuizModeQueueHandler.TimeoutHandler(context, publicMessageHandler)
			
			self.commandHandlerStack = [publicMessageHandler, AdminMessageHandler(context), namReplyHandler, exitHandler,
				endOfNamesHandler, ReadyToJoinHandler(context), EndOfMOTDHandler(context), PingHandler(context), onUserJoinHandler,
				onUserLeaveHandler, timeoutHandler]

	__instance = None
	
	def __init__(self, context):
		if not self.__instance:
			QuizModeQueueHandler.__instance = QuizModeQueueHandler.__QuizModeQueueHandler(context)
			
	def handleCommand(self, command):
		for handler in self.__instance.commandHandlerStack:
			if handler.run(command):
				return