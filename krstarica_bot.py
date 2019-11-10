from context import *
from quiz_plugin import *

context = Context('irc.krstarica.com', 6667, '#slagalica-kviz', 'kviz_supervizor', 'teslaboys1994', 'miloss')
plugin = QuizPlugin(context)

plugin.initBaseHandlers()
plugin.start()