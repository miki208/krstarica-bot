from enum import Enum
from IO import FileInputAdapter, FileOutputAdapter
from random import randint, shuffle, choice
from Helpers import print_unicode
from threading import Timer

class Quiz:
	class GameState(Enum):
		UNINITIALIZED = 0
		INITIALIZED = 1
		TIMEOUT = 2
		NEW_PUZZLE = 3
		NOT_ENOUGH_PLAYERS = 4
		ENOUGH_PLAYERS = 5
		GAME_FINISHED = 6
		ROUND_FINISHED = 7
	
	def __init__(self, handler):
		self.observer = handler
		self.__wordsInputAdapter = FileInputAdapter('words_new.txt')
		self.__allWordsInputAdapter = FileInputAdapter('all_words_new.txt')
		self.__usersInputAdapter = FileInputAdapter('users.txt')
		self.__usersOutputAdapter = FileOutputAdapter('users.txt')
		self.__state = Quiz.GameState.UNINITIALIZED
		self.__timer = Timer(30, self.onTimeout)
		self.__users = dict()
		self.__onlineUsers = []
		self.__usersCount = 0
		self.__currentWord = ""
		self.__currentPuzzle = ""
		
	def getGamesPlayed(self):
		return self.__gamesPlayed
		
	def startNewGame(self):
		self.__gamesPlayed = 0
		for user in self.__onlineUsers:
			self.__fillUserInfo(user, self.__users[user]['credit'], 0, False)
		self.generateNewWord()
		
	def onClose(self):
		self.cancelTimer()
		self.__saveUsers()
		
	def loadGame(self):
		self.__loadWords()
		self.__loadUsers()
		
		self.setState(Quiz.GameState.INITIALIZED)
		self.__checkPlayers()
		
	def __loadWords(self):
		self.__allWordsInputAdapter.open()
		self.__allWords = self.__allWordsInputAdapter.readAll()
		self.__allWordsInputAdapter.close()
		
		self.__wordsInputAdapter.open()
		self.__words = self.__wordsInputAdapter.readAll()
		self.__wordsInputAdapter.close()
		
	def __shuffleLetters(self, word):
		letters = ['a', 'b', 'v', 'g', 'd', 'đ', 'e', 'ž', 'z', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'ć', 'č', 'u', 'f', 'h', 'c', 'š']
			
		temp = list(word)
		shuffle(temp)
		
		templen = len(temp)
		for i in range(0, 14 - len(temp)):
			temp.append(choice(letters))
			
		return ''.join(temp)
		
	def generateNewWord(self):
		self.__currentWord = self.__words[randint(0, len(self.__words) - 1)]
		self.__currentPuzzle = self.__shuffleLetters(self.__currentWord)
		
		self.setState(Quiz.GameState.NEW_PUZZLE)
		self.__timer = Timer(30, self.onTimeout)
		self.__timer.start()
		
	def onTimeout(self):
		self.setState(Quiz.GameState.TIMEOUT)
		
	def cancelTimer(self):
		self.__timer.cancel()
		
	def getPuzzle(self):
		return self.__currentPuzzle
		
	def getWord(self):
		return self.__currentWord
		
	def onUserJoin(self, user):
		if self.observer.context.botNick == user:
			return
		
		if user in self.__users:
			self.observer.context.send_msg("10,15Korisnik 04" + user + "10 se pridružio. On ima 04" + str(self.__users[user]['credit']) + "10 kredita.")
			self.__fillUserInfo(user, self.__users[user]['credit'], 0, False)
		else:
			self.observer.context.send_msg("10,15Korisnik 04" + user + "10 se pridružio. On je novajlija :)")
			self.__setUpNewUser(user)
			
		self.__onlineUsers.append(user)
		
		self.__usersCount = self.__usersCount + 1
		self.__checkPlayers()
		
	def __setUpNewUser(self, user):
		self.__users[user] = dict()
		self.__fillUserInfo(user, 0, 0, False)
		
	def onUserLeave(self, user):
		self.__usersCount = self.__usersCount - 1
		self.__onlineUsers.remove(user)
		self.__checkPlayers()
		
	def setState(self, state):
		if self.__state == state:
			return
			
		if self.__state == Quiz.GameState.NEW_PUZZLE and state == Quiz.GameState.ENOUGH_PLAYERS:
			return
		
		self.__state = state
		self.observer.update()
		
	def getState(self):
		return self.__state
		
	def __loadUsers(self):
		self.__usersInputAdapter.open()
		temp = self.__usersInputAdapter.readAll()
		self.__usersInputAdapter.close()
		
		for t in temp:
			tokens = t.split(' ')
			self.__users[tokens[0]] = dict()
			self.__fillUserInfo(tokens[0], int(tokens[1]), 0, False)
			
	def __fillUserInfo(self, userNick, credit, points, answered):
		self.__users[userNick]['credit'] = credit
		self.__users[userNick]['points'] = points
		self.__users[userNick]['answered'] = answered
			
	def __saveUsers(self):
		lines = []
		for key, value in self.__users.items():
			lines.append(key + ' ' + str(value['credit']))
		self.__usersOutputAdapter.open()
		self.__usersOutputAdapter.updateAll(lines)
		self.__usersOutputAdapter.close()
		
	def setUsers(self, users):
		for user in users:
			if self.observer.context.botNick == user:
				continue
				
			if user not in self.__users:
				self.__setUpNewUser(user)
			self.__onlineUsers.append(user)
			
		self.__usersCount = len(users) - 1
		
	def __checkPlayers(self):
		if self.getState() == Quiz.GameState.UNINITIALIZED:
			return
	
		if self.__usersCount < 2:
			self.setState(Quiz.GameState.NOT_ENOUGH_PLAYERS)
		else:
			self.setState(Quiz.GameState.ENOUGH_PLAYERS)
			
	def checkAnswer(self, user, answer):
		if self.getState() == Quiz.GameState.TIMEOUT:
			self.observer.context.send_notice(user, '04,15Vreme za rešavanje je isteklo. Sačekajte sledeću rundu.')
			return
		elif self.getState() != Quiz.GameState.NEW_PUZZLE:
			self.observer.context.send_notice(user, '04,15Kviz trenutno nije aktivan. Pokušajte ponovo kasnije.')
			return
		
		if self.__users[user]['answered']:
			self.observer.context.send_notice(user, '04,15Već ste poslali rešenje za ovaj zadatak.')
			return
	
		sortedPuzzle = sorted(self.__currentPuzzle)
		sortedAnswer = sorted(answer)
		
		print_unicode("ans " + str(sortedAnswer))
		print_unicode("puz " + str(sortedPuzzle))
		
		i = 0
		for ca in sortedAnswer:
			if i == 14:
				self.observer.context.send_notice(user, '04,15Iskoristili ste slova koja nisu dostupna.')
				self.__users[user]['answered'] = True
				return
				
			while i < 14:
				if ca == sortedPuzzle[i]:
					i = i + 1
					break
				i = i + 1
		
		self.__users[user]['answered'] = True
		
		if answer in self.__allWords:
			points =  ((min(len(answer), 14) / len(self.getWord())) * 30 \
				+ 4 * max(0, len(answer) - len(self.__currentWord)) + 5 * int(answer == self.__currentWord)) // 1
				
			self.__users[user]['points'] += points
				
			self.observer.context.send_notice(user, '03,15Vaše rešenje je prihvaćeno. Osvojili ste 04' + str(points) + '03 poena.')
		else:
			self.observer.context.send_notice(user + '04,15 Vaše rešenje nije prihvaćeno.')
			
	def startNewRound(self):
		self.__gamesPlayed = self.__gamesPlayed + 1
		for user in self.__onlineUsers:
			self.__fillUserInfo(user, self.__users[user]['credit'], self.__users[user]['points'], False)
		self.generateNewWord()
	
	def onRoundFinished(self):
		self.__onlineUsers.sort(key = lambda us, allus = self.__users: allus[us]['points'], reverse = True)
		
		if self.getGamesPlayed() == 3:	
			top3Message = '10,15[KRAJ PARTIJE] Top 3 u ovoj partiji: '
		else:
			top3Message = '10,15Top 3 u ovoj rundi: '
			
		for i in range(0, 3):
			if i >= self.__usersCount:
				break
					
			tmpNick = self.__onlineUsers[i]
			points = self.__users[tmpNick]['points']
			
			if self.getGamesPlayed() == 3:
				credit = int(points > 0) * (5 - 2 * i)
				top3Message += '4' + tmpNick + '10(04' + str(points) + 'p10)[4+' + str(credit) + '$10] | '
				self.__users[tmpNick]['credit'] += credit
			else:
				top3Message += '4' + tmpNick + '10(04' + str(points) +'p10) | '
				
		return top3Message
		
	def getCredit(self, user):
		return self.__users[user]['credit']
		
	def getPuzzlePrint(self):
		return "10,15(04" + str(self.getGamesPlayed() + 1) + "10/04410) ZADATAK: 04" + ' '.join(list(self.getPuzzle()))
		
	def getHelpPrint(self):
		return ["10,15Ovo je kviz baziran na prvoj igri popularnog kviza slagalica.", 
				"10,15Slova 04l10, 04j10 i 04n10 se mogu koristiti u kombinaciji kao slova 04lj10 i 04nj10.",
				"10,15Svaka partija se sastoji od 04410 runde. Prva 04310 igrača na kraju partije dobijaju kredite.",
				"10,15Komande:",
				"04,15!odgovor [vaš odgovor]10 ili 04!o [vaš odgovor]10 - slanje vašeg odgovora",
				"04,15!zadatak10 ili 04!z10 - provera tekućeg zadatka",
				"04,15!top510 - provera 5 igrača sa najvećim kreditom",
				"04,15!kredit10 - provera Vašeg kredita",
				"04,15!help10 - pročitajte pomoć"]
				
	def getTop5Print(self):
		message = "10,15Top 04510: "
		rank = sorted(self.__users.items(), key = lambda data: data[1]['credit'], reverse = True)

		for i in range(0, 5):
			if i == len(rank):
				break
			message += str(i + 1) + ". 04" + rank[i][0] + "10 (04" + str(rank[i][1]['credit']) + "$10) | "
		
		return message