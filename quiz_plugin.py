from base_plugin import *
from slagalica import *
from moj_broj import *
from state import *
from model import *
from IO import *

class QuizPlugin(BasePlugin):
	def __init__(self, context):
		super(QuizPlugin, self).__init__(context, "Slagalica kviz")

		self._gameEventSource = EventSource()
		self._gameEventSource.registerEvent(QuizState.NOT_INITIALIZED, None)
		self._gameEventSource.registerEvent(QuizState.INITIALIZED, None)
		self._gameEventSource.registerEvent(QuizState.GAME_1, None)
		self._gameEventSource.registerEvent(QuizState.GAME_2, None)
		self._gameEventSource.registerEvent(QuizState.WAIT_FOR_PLAYERS, None)
		self._gameEventSource.registerEvent(QuizState.INTERRUPT_CURRENT_GAME, None)
		self._gameEventSource.registerEvent(QuizState.STOPPED, None)
		self._gameEventSource.registerEvent(QuizState.MATCH_FINISHED, None)
		self._gameEventSource.registerHandler(QuizState.NOT_INITIALIZED, self.__onGameNotInitialized)
		self._gameEventSource.registerHandler(QuizState.INITIALIZED, self.__onGameInitialized)
		self._gameEventSource.registerHandler(QuizState.GAME_1, self.__onGame1Started)
		self._gameEventSource.registerHandler(QuizState.GAME_2, self.__onGame2Started)
		self._gameEventSource.registerHandler(QuizState.WAIT_FOR_PLAYERS, self.__onWaitForPlayers)
		self._gameEventSource.registerHandler(QuizState.INTERRUPT_CURRENT_GAME, self.__onInterruptCurrentGame)
		self._gameEventSource.registerHandler(QuizState.STOPPED, self.__onStop)
		self._gameEventSource.registerHandler(QuizState.MATCH_FINISHED, self.__onMatchFinished)

		self._state = State(self._gameEventSource, QuizState.NOT_INITIALIZED)
		self._users = dict()
		self._onlineUsers = 0
		self._games = dict()
		self._currentGame = None

	#game specific handlers
	def __onResultsReady(self, *data):
		nextState = self.__getNextGameState()

		for player in data[0]:
			self._context.send_notice(player.username, "10,15 U ovoj igri ste osvojili 05,15\x02\x11" +\
				str(player.points) + "10,15 poena.")

			if player.username in self._players.keys():
				self._players[player.username].points += player.points
			else:
				self._players[player.username] = User(player.username, player.points)

		if nextState != QuizState.MATCH_FINISHED and len(self._players) != 0:
			self._context.send_msg('10,15Rezultati na kraju ove igre: 02,15\x02\x11' +\
				', '.join([str(x) for x in self._players.values()]))

		self._currentGame.getState().setState(GameState.READY_TO_START)

		self._state.setState(nextState)

	#quiz state handlers
	def __onGameNotInitialized(self, *data):
		self._context.send_msg("10,08\x1DUčitavam ovu strava igricu...")

		file = FileInputAdapter('users.txt')
		file.open()
		fileContent = file.readAll()
		file.close()

		for line in fileContent:
			tokens = line.split(' ')
			self._users[tokens[0]] = User(tokens[0], int(tokens[1]))

		for user in data[0]:
			if user not in self._users.keys():
				self._users[user] = User(user, 0)
				self._context.send_notice(user, '10,08\x1DPrimetili smo da ste novi igrač. Dobro nam došli! :)')

		self._onlineUsers = len(data[0])

		#initialize games
		self._games['slagalica'] = Slagalica(self._context)
		self._games['slagalica'].getEventSource().registerHandler(GameState.RESULTS_READY, self.__onResultsReady)
		self._games['slagalica'].initState()
		self._games['moj_broj'] = MojBroj(self._context)
		self._games['moj_broj'].getEventSource().registerHandler(GameState.RESULTS_READY, self.__onResultsReady)
		self._games['moj_broj'].initState()

		self._state.setState(QuizState.INITIALIZED)

	def __onGameInitialized(self, *data):
		self._context.send_msg("10,08\x1DIgrica je učitana, uživajte!")

		self._state.setState(QuizState.WAIT_FOR_PLAYERS)

	def __onGame1Started(self, *data):
		self._players = dict()
		self._currentGame = self._games['slagalica']
		self._currentGame.getState().setState(GameState.GENERATE_TASK)

	def __onGame2Started(self, *data):
		self._currentGame = self._games['moj_broj']
		self._currentGame.getState().setState(GameState.GENERATE_TASK)

	def __onWaitForPlayers(self, *data):
		if self._onlineUsers >= 2:
			self._context.send_msg("10,15Započinjem novu partiju.")
			self._state.setState(QuizState.GAME_1)
		else:
			self._context.send_msg("05,15Potrebna su bar dva igrača kako bih započeo partiju.")

	def __onInterruptCurrentGame(self, *data):
		self._context.send_msg("05,15Više nema dovoljno igrača. Prekidam partiju.")
		self._currentGame.getState().setState(GameState.READY_TO_START)
		self._currentGame = None

		self._state.setState(QuizState.WAIT_FOR_PLAYERS)

	def __onStop(self, *data):
		pass

	def __onMatchFinished(self, *data):
		if len(self._players) != 0:
			self._context.send_msg('10,15Rezultati na kraju ove partije: 02,15\x02\x11' +\
				', '.join([str(x) for x in self._players.values()]))

		for player in self._players.values():
			self._users[player.username].points += player.points

		self._context.send_msg('\x0305,15-----------------------------')

		self._state.setState(QuizState.WAIT_FOR_PLAYERS)

	#base handlers
	def onRoomInitialized(self, users):
		users = list(filter(lambda user: True if user != self._context.botNick else False, users))
		self._state.setState(QuizState.NOT_INITIALIZED, users)

	def onExit(self):
		lines = []

		for key, value in self._users.items():
			lines.append(key + ' ' + str(value.points))

		file = FileOutputAdapter('users.txt')
		file.open()
		file.updateAll(lines)
		file.close()

	def onAdminCommand(self, command):
		print(command)

	def onExitCommand(self):
		self._context.send_msg("05,08\x1DIgrica je zaustavljena!")

		if self.isInGame():
			self._currentGame.getState().setState(GameState.READY_TO_START)
			self._currentGame = None

		self._state.setState(QuizState.STOPPED)

	def onUserLeave(self, user):
		self._onlineUsers -= 1
		if self._onlineUsers < 2 and self.isInGame():
			self._state.setState(QuizState.INTERRUPT_CURRENT_GAME)

	def onUserJoin(self, user):
		if self._state.getState() == QuizState.NOT_INITIALIZED or self._state.getState() == QuizState.INITIALIZED:
			return

		if user not in self._users.keys():
			self._context.send_msg("10,08Korisnik 05,08" + user + "10,08 se pridružio. On je novajlija :)")
			self._users[user] = User(user, 0)
		else:
			self._context.send_msg("10,08Korisnik 05,08" + user + "10,08 se pridružio. On ima 05,08\x02\x11" +\
			str(self._users[user].points) + "10,08 poena.")

		self._onlineUsers += 1
		if self._onlineUsers >= 2 and self._state.getState() == QuizState.WAIT_FOR_PLAYERS:
			self._context.send_msg("10,15U redu, sada ima dovoljno igrača. Započinjem novu partiju.")
			self._state.setState(QuizState.GAME_1)			

	def onPublicMessage(self, user, message):
		if self.isInGame():
			self._currentGame.onMessageReceived(user, message)

	def onInternalMessage(self, message):
		if self.isInGame() and len(message) == 1 and message[0] == ':TIMEOUT':
			self._currentGame.onTimeout()

	#helpers
	def isInGame(self):
		if not self._currentGame:
			return False

		state = self._state.getState()
		if state == QuizState.GAME_1:
			return True
		if state == QuizState.GAME_2:
			return True

		return False

	def __getNextGameState(self):
		if not self.isInGame():
			return QuizState.WAIT_FOR_PLAYERS

		state = self._state.getState()
		if state == QuizState.GAME_1:
			return QuizState.GAME_2
		if state == QuizState.GAME_2:
			return QuizState.MATCH_FINISHED