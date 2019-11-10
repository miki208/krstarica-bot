from enum import Enum

class State:
	def __init__(self, eventSource, initialState):
		self._eventSource = eventSource
		self._state = initialState

	def setState(self, newState, *data):
		self._state = newState
		self._eventSource.triggerEvent(newState, *data)

	def getState(self):
		return self._state

class QuizState(Enum):
	NOT_INITIALIZED = 1
	INITIALIZED = 2
	GAME_1 = 3
	WAIT_FOR_PLAYERS = 4
	INTERRUPT_CURRENT_GAME = 5
	STOPPED = 6
	MATCH_FINISHED = 7
	GAME_2 = 8

class GameState(Enum):
	NOT_INITIALIZED = 1
	READY_TO_START = 2
	GENERATE_TASK = 3
	GAME_STARTED = 4
	TIMEOUT = 5
	RESULTS_READY = 6