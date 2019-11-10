from IO import *
from game import *
from model import *
from random import randint, shuffle, choice
from math import ceil

class Slagalica(Game):
	def __init__(self, context):
		super(Slagalica, self).__init__(context, "Slagalica")

	def onNotInitialized(self, *data):
		file = FileInputAdapter("words.txt")
		file.open()
		self._words = file.readAll()
		file.close()

		file = FileInputAdapter("all_words.txt")
		file.open()
		self._all_words = file.readAll()
		file.close()

		super(Slagalica, self).onNotInitialized(*data)

	def onReadyToStart(self, *data):
		super(Slagalica, self).onReadyToStart(*data)

		self._players = dict()
		self._currentWord = ""
		self._currentTask = ""
		self._usedWords = []

	def onGenerateTask(self, *data):
		super(Slagalica, self).onGenerateTask(*data)

		self._currentWord = self._words[randint(0, len(self._words) - 1)] #generate our word
		self._currentTask = self.__shuffleLetters(self._currentWord) #generate a task
		self._state.setState(GameState.GAME_STARTED) #start the game

	def onGameStarted(self, *data):
		super(Slagalica, self).onGameStarted(*data)

		self._context.send_msg("10,15Ponuđena slova su: \x0305,15\x02\x11" + ' '.join(list(self._currentTask.upper())))
		self._context.send_msg("10,15Imate 05,15\x02\x11" + str(self._duration) + "10,15 sekundi za rešavanje.")

	def onTimeout(self):
		self._context.send_msg("10,15 Naša reč je bila 05,15\x02\x11" + self._currentWord)

		results = []
		count = 0

		#count all the letters from all answers
		for player in self._players.values():
			if player.answer:
				count += len(player.answer)

		#calculate points proportionally
		for player in self._players.values():
			if player.answer:
				player.points = ceil(30.0 * len(player.answer) / count)
				results.append(User(player.username, player.points))

		self._state.setState(GameState.RESULTS_READY, results)

	def onMessageReceived(self, user, msg):
		if self._state.getState() == GameState.GAME_STARTED:
			if len(msg) == 2 and msg[0] == ':!odgovor':
				answer = msg[1]

				if user not in self._players.keys():
					self._players[user] = Player(user, None, 0)

					if not self.__checkLetters(answer, self._currentTask):
						self._context.send_notice(user, "05,15Iskoristili ste slova koja nisu dostupna. :(")
						return

					if answer in self._usedWords:
						del self._players[user] #give him another chance
						self._context.send_notice(user, "05,15Neko je već iskoristio ovu reč. Pokušajte sa nekom drugom.")
						return

					if answer in self._all_words:
						self._players[user].answer = answer
						self._usedWords.append(answer)
						self._context.send_notice(user, "03,15Vaša reč je prihvaćena, čestitamo! :)")
						return
					else:
						self._context.send_notice(user, "05,15Nažalost, ne možemo da prihvatimo vašu reč. :(")
				else:
					self._context.send_notice(user, "05,15Već ste poslali Vaš odgovor. Sačekajte sledeću igru. :)" )
					return

	def __shuffleLetters(self, word):
		letters = ['a', 'b', 'v', 'g', 'd', 'đ', 'e', 'ž', 'z', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'ć', 'č', 'u', 'f', 'h', 'c', 'š']
			
		temp = list(word)
		shuffle(temp)
		
		templen = len(temp)
		for i in range(0, 14 - len(temp)):
			temp.append(choice(letters))
			
		return ''.join(temp)

	def __checkLetters(self, answer, task):
		sortedTask = sorted(task)
		sortedAnswer = sorted(answer)

		i = 0
		for c in sortedAnswer:
			if i == 14:
				return False
			while i < 14:
				if c == sortedTask[i]:
					i = i + 1
					break
				i = i + 1

		return True