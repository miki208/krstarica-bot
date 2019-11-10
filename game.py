from event_source import EventSource
from state import *

from threading import Timer

class Game:
	def __init__(self, context, name):
		self._context = context
		self._name = name
		self._eventSource = EventSource()
		self._timer = None
		self._duration = 60

		self._eventSource.registerEvent(GameState.NOT_INITIALIZED, None)
		self._eventSource.registerEvent(GameState.READY_TO_START, None)
		self._eventSource.registerEvent(GameState.GENERATE_TASK, None)
		self._eventSource.registerEvent(GameState.GAME_STARTED, None)
		self._eventSource.registerEvent(GameState.TIMEOUT, None)
		self._eventSource.registerEvent(GameState.RESULTS_READY, None)

		self._eventSource.registerHandler(GameState.NOT_INITIALIZED, self.onNotInitialized)
		self._eventSource.registerHandler(GameState.READY_TO_START, self.onReadyToStart)
		self._eventSource.registerHandler(GameState.GENERATE_TASK, self.onGenerateTask)
		self._eventSource.registerHandler(GameState.GAME_STARTED, self.onGameStarted)
		self._eventSource.registerHandler(GameState.TIMEOUT, self.__onTimeoutInternal)

		self._state = State(self._eventSource, GameState.NOT_INITIALIZED)

	def initState(self):
		self._state.setState(GameState.NOT_INITIALIZED)

	def getEventSource(self):
		return self._eventSource

	def getState(self):
		return self._state

	#game handlers
	def onNotInitialized(self, *data):
		self._state.setState(GameState.READY_TO_START)

	def onReadyToStart(self, *data):
		if self._timer:
			self._timer.cancel()
			self._timer = None

	def onGenerateTask(self, *data):
		self._context.send_msg("10,15Sledeća igra: 05,15\x02\x11" + self._name)

	def onGameStarted(self, *data):
		self._timer = Timer(self._duration, lambda: self._state.setState(GameState.TIMEOUT))
		self._timer.start()

	def __onTimeoutInternal(self, *data):
		self._context.send_msg("10,15Vreme je isteklo")
		self._context.send_notice(self._context.botNick, 'TIMEOUT')

	#external events
	def onMessageReceived(self, user, message):
		pass

	def onTimeout(self):
		pass