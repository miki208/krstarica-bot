class User:
	def __init__(self, username, points):
		self.username = username
		self.points = points

	def __str__(self):
		return self.username + " (" + str(self.points) + ")"

class Player:
	def __init__(self, username, answer, points):
		self.username = username
		self.answer = answer
		self.points = points