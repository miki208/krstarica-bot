class AbstractInputAdapter:
	def __init__(self):
		pass
		
	def readAll(self):
		pass
		
	def readNext(self):
		pass
		
	def read(self, id):
		pass
		
	def open(self):
		pass
		
	def close(self):
		pass
		
class AbstractOutputAdapter:
	def __init__(self):
		pass
		
	def updateAll(self, data):
		pass
		
	def update(self, id, row):
		pass
	
	def add(self, id, row):
		pass
		
	def open(self):
		pass
		
	def close(self):
		pass
		
class FileOutputAdapter(AbstractOutputAdapter):
	def __init__(self, filename):
		super(FileOutputAdapter, self).__init__()
		self.__filename = filename
		self.__file = None

	def updateAll(self, data):
		if self.__file is None:
			raise ValueError("File isn't opened.'")
			
		for line in data:
			self.__file.write(line + '\n')
			
	def update(self, id, row):	
		if self.__file is None:
			raise ValueError("File isn't opened.'")
			
		lines = self.__file.readlines()
		for i, line in enumerate(lines):
			if i == id:
				self.__file.write(row + '\n')
			else:
				self.__file.write(line)
	
	def add(self, id, row):
		if self.__file is None:
			raise ValueError("File isn't opened.'")
			
		lines = self.__file.readlines()
		for i, line in enumerate(lines):
			if i == id:
				self.__file.write(row + '\n')
			self.__file.write(line)
	
	def open(self):
		if self.__file == None:
			self.__file = open(self.__filename, 'w+', encoding = 'utf8')
	
	def close(self):
		if self.__file is not None:
			self.__file.close()
			self.__file = None
			
	def getFilename(self):
		return self.__filename
	
class FileInputAdapter(AbstractInputAdapter):
	def __init__(self, filename):
		super(FileInputAdapter, self).__init__()
		self.__filename = filename
		self.__file = None
		
	def getFilename(self):
		return self.__filename
		
	def open(self):
		if self.__file == None:
			self.__file = open(self.__filename, 'r', encoding = 'utf8')
			
	def close(self):
		if self.__file is not None:
			self.__file.close()
			self.__file = None
			
	def readAll(self):
		if self.__file is None:
			raise ValueError("File isn't opened.'")
	
		self.__file.seek(0, 0)
		return [x.strip() for x in self.__file] 
		
	def readNext(self):
		if self.__file is None:
			raise ValueError("File isn't opened.'")
			
		return self.__file.readline()
		
	def read(self, id):
		if self.__file is None:
			raise ValueError("File isn't opened.'")
			
		self.__file.seek(0, 0)
		
		for i, line in enumerate(self.__file):
			if i == id:
				return line.strip()
				
		return ""