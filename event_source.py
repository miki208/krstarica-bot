from helpers import *

class EventSource:
	def __init__(self):
		self._events = []
		self._handlers = dict()
		self._firstHandlerAdded = False

	def registerEvent(self, eventName, eventFilter):
		self._events.append((eventName, eventFilter))

	def registerHandler(self, eventName, callback):
		if not self._firstHandlerAdded:
			self._firstHandlerAdded = True
			for eName, eventFilter in self._events:
				self._handlers[eName] = []

		self._handlers[eventName].append(callback)

	def triggerEvent(self, event, *eventData):
		for handler in self._handlers[event]:
			handler(*eventData)

class IRCEventSource(EventSource):
	def __init__(self, context):
		super(IRCEventSource, self).__init__()
		self._context = context

	def start(self):
		self._context.connect()
		
		while True:
			command = prepare_data(self._context.get_next_line())

			for eventName, eventFilter in self._events:
				if eventFilter(command):
					for handler in self._handlers[eventName]:
						handler(*command)
					break