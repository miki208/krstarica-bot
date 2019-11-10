from event_source import *
from helpers import *

class BasePlugin:
	def __init__(self, context, pluginName):
		self._context = context
		self._pluginName = pluginName
		self.__users = []
		self._ircEventSource = IRCEventSource(context)

		self._ircEventSource.registerEvent('on-exit', self._on_exit_filter)
		self._ircEventSource.registerEvent('on-end-of-names', self._on_end_of_names_filter),
		self._ircEventSource.registerEvent('on-nam-reply', self._on_nam_reply_filter),
		self._ircEventSource.registerEvent('on-user-join', self._on_user_join_filter),
		self._ircEventSource.registerEvent('on-user-leave', self._on_user_leave_filter),
		self._ircEventSource.registerEvent('on-ready-to-join', self._on_ready_to_join_filter),
		self._ircEventSource.registerEvent('on-end-of-motd', self._on_end_of_motd_filter),
		self._ircEventSource.registerEvent('on-ping', self._on_ping_filter),
		self._ircEventSource.registerEvent('on-admin-message', self._on_admin_message_filter),
		self._ircEventSource.registerEvent('on-public-message', self._on_public_message_filter)
		self._ircEventSource.registerEvent('on-internal-message', self._on_internal_message_filter)
		self._ircEventSource.registerEvent('on-message', self._on_message_filter)

	def initBaseHandlers(self):
		self._ircEventSource.registerHandler('on-exit', self._onExitBase)
		self._ircEventSource.registerHandler('on-ready-to-join', self._onReadyToJoinBase)
		self._ircEventSource.registerHandler('on-end-of-motd', self._onEndOfMotdBase)
		self._ircEventSource.registerHandler('on-ping', self._onPingBase)
		self._ircEventSource.registerHandler('on-admin-message', self._onAdminCommandBase)
		self._ircEventSource.registerHandler('on-end-of-names', self._onEndOfNamesBase)
		self._ircEventSource.registerHandler('on-nam-reply', self._onNamReplyBase)
		self._ircEventSource.registerHandler('on-user-leave', self._onUserLeaveBase)
		self._ircEventSource.registerHandler('on-user-join', self._onUserJoinBase)
		self._ircEventSource.registerHandler('on-public-message', self._onPublicMessageBase)
		self._ircEventSource.registerHandler('on-internal-message', self._onInternalMessageBase)

	def start(self):
		self._ircEventSource.start()

	#handlers for overriding
	def onRoomInitialized(self, users):
		pass

	def onExit(self):
		pass

	def onExitCommand(self):
		pass

	def onAdminCommand(self, command):
		pass

	def onUserLeave(self, user):
		pass

	def onUserJoin(self, user):
		pass

	def onPublicMessage(self, user, msg):
		pass

	def onInternalMessage(self, msg):
		pass

	#handlers for plugin initialization
	def _onExitBase(self, *args):
		self.onExit()
		exit()

	def _onReadyToJoinBase(self, *args):
		self._context.send_data("JOIN " + self._context.channel + "\n")

	def _onEndOfMotdBase(self, *args):
		self._context.send_data("NS IDENTIFY " + self._context.botPassword + "\n")

	def _onPingBase(self, *args):
		self._context.send_data("PONG " + args[1] + "\n")

	def _onAdminCommandBase(self, *args):
		if ' '.join(args[3:]) == ':QUIT':
			self.onExitCommand()
			self._context.send_data("QUIT Goodbye!\n")
		else:
			self.onAdminCommand(list(args[3:]))

	def _onEndOfNamesBase(self, *args):
		self.onRoomInitialized(self.__users)

	def _onNamReplyBase(self, *args):
		command = list(args)
		command[5] = command[5][1:]
		self.__users = [x if x[0] not in ['%', '@', '+'] else x[1:] for x in command[5:]]

	def _onUserLeaveBase(self, *args):
		self.onUserLeave(getName(args[0]))

	def _onUserJoinBase(self, *args):
		self.onUserJoin(getName(args[0]))

	def _onPublicMessageBase(self, *args):
		self.onPublicMessage(getName(args[0]), list(args[3:]))

	def _onInternalMessageBase(self, *args):
		self.onInternalMessage(list(args[3:]))

	#filters
	def _on_exit_filter(self, command):
		return command[0] == 'ERROR'

	def _on_end_of_names_filter(self, command):
		return command[1] == '366' and\
			command[2] == self._context.botNick and\
			command[3] == self._context.channel

	def _on_nam_reply_filter(self, command):
		return command[1] == '353' and\
			command[2] == self._context.botNick and\
			command[4] == self._context.channel

	def _on_user_join_filter(self, command):
		return command[1] == 'JOIN' and command[2][1:] == self._context.channel

	def _on_user_leave_filter(self, command):
		return (command[1] == 'PART' and command[2] == self._context.channel) or (command[1] == 'QUIT')

	def _on_ready_to_join_filter(self, command):
		return command[0] == ':irc.krstarica.com' and command[1] == 'NOTICE' and\
			command[2] == self._context.botNick and ' '.join(command[3:]).startswith(':Pristup Vam je dozvoljen!')

	def _on_end_of_motd_filter(self, command):
		return command[1] == '376' or command[1] == '422'

	def _on_ping_filter(self, command):
		return command[0] == 'PING'

	def _on_message_filter(self, command):
		return len(command) >= 2 and command[1] == 'PRIVMSG'

	def _on_public_message_filter(self, command):
		return self._on_message_filter(command) and command[2] == self._context.channel

	def _on_admin_message_filter(self, command):
		return self._on_message_filter(command) and\
			getName(command[0]) == self._context.adminNick and\
			command[2] == self._context.botNick

	def _on_internal_message_filter(self, command):
		return getName(command[0]) == self._context.botNick and\
			command[1] == 'NOTICE' and\
			command[2] == self._context.botNick