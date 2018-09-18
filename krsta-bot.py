from CommandQueueHandler import QueueHandlerFactory
from Helpers import Context, prepare_data

context = Context('irc.krstarica.com', 6667, '#slagalica-kviz', 'kviz_supervizor', 'password', 'botname')
handler = QueueHandlerFactory('quiz', context)
	
context.connect()
	
while True:
	handler.handleCommand(prepare_data(context.get_next_line()))