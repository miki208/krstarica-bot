import re
from game import *
from model import *
from random import randint
from math import ceil
from py_expression_eval import Parser

class MojBroj(Game):
	def __init__(self, context):
		super(MojBroj, self).__init__(context, "Moj broj")

		self._parser = Parser()
		self._reValidMathExpression = re.compile(r"^(?:[0-9]+|\*|\+|-|/| |\(|\))+$")
		self._reValidNumber = re.compile(r"[0-9]+")

	def onNotInitialized(self, *data):
		super(MojBroj, self).onNotInitialized(*data)

	def onReadyToStart(self, *data):
		super(MojBroj, self).onReadyToStart(*data)

		self._players = dict()
		self._answers = [] #list of tuples (id of answer, answer, username)
		self._counter = 0

	def onGenerateTask(self, *data):
		super(MojBroj, self).onGenerateTask(*data)

		self._currentTask = [[]]

		for i in range(0, 4):
			self._currentTask[0].append(randint(1, 9))
		self._currentTask[0].append([10, 15, 20][randint(0, 2)])
		self._currentTask[0].append([25, 50, 75, 100][randint(0, 3)])
		self._currentTask[0] = sorted(self._currentTask[0])

		self._currentTask.append(randint(1, 999))

		self._state.setState(GameState.GAME_STARTED) #start the game

	def onGameStarted(self, *data):
		super(MojBroj, self).onGameStarted(*data)

		self._context.send_msg("10,15Traži se broj \x0305,15\x02\x11" + str(self._currentTask[1]) +\
			"\x0310,15. Ponuđeni brojevi su:\x0305,15 \x02\x11" + ' '.join([str(x) for x in self._currentTask[0]]))
		self._context.send_msg("10,15Imate 05,15\x02\x11" + str(self._duration) + "10,15 sekundi za rešavanje.")

	def onTimeout(self):
		results = []

		self._answers = sorted(self._answers, key = lambda elem: (abs(elem[1] - self._currentTask[1]), elem[0]))

		numOfAnswers = len(self._answers)
		if numOfAnswers != 0:
			minPoints = ceil(30.0 / (numOfAnswers * (numOfAnswers + 1) / 2))
		points = [x for x in range(1, numOfAnswers)]

		for i, elem in enumerate(self._answers):
			self._players[elem[2]].points = (numOfAnswers - i) * minPoints
			results.append(User(self._players[elem[2]].username, self._players[elem[2]].points))

		self._state.setState(GameState.RESULTS_READY, results)

	def onMessageReceived(self, user, msg):
		if self._state.getState() == GameState.GAME_STARTED:
			if msg[0] == ':!odgovor':
				answer = ''.join(msg[1])

				if user not in self._players.keys():
					self._players[user] = Player(user, None, 0)

					numbers = self.__checkExpressionAndGetNumbers(answer)
					print(numbers)
					if numbers != None:
						if not self.__checkAreNumbersValid(numbers, self._currentTask[0]):
							self._context.send_notice(user, "05,15Iskoristili ste brojeve koji nisu dostupni. :(")
							return
						try:
							exprVal = self._parser.parse(answer).evaluate({})
							self._players[user].answer = exprVal
							self._answers.append((self._counter, exprVal, user))
							self._counter += 1
							self._context.send_notice(user, "03,15Vaš izraz je prihvaćen, dobili ste broj \x0305,15\x02\x11" +\
								str(exprVal) + "\x0303,15! :)")
						except:
							self._context.send_notice(user, "05,15Nažalost, ne možemo da prihvatimo vaš izraz. :(")
							return
					else:
						self._context.send_notice(user, "05,15Nažalost, ne možemo da prihvatimo vaš izraz. :(")
						return
				else:
					self._context.send_notice(user, "05,15Već ste poslali Vaš odgovor. Sačekajte sledeću igru. :)" )
					return

	def __checkExpressionAndGetNumbers(self, expression):
		result = self._reValidMathExpression.match(expression)
		if not result:
			return None

		return [int(x) for x in self._reValidNumber.findall(expression)]

	def __checkAreNumbersValid(self, answer, task):
		i = 0
		answer = sorted(answer)
		task = sorted(task)
		for num in answer:
			if i == len(task):
				return False
			while i < len(task):
				if num == task[i]:
					i = i + 1
					break
				i = i + 1

		return True