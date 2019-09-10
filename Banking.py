class person():
	def __init__(self, name, age, sex):
		
		self.name  = name
		self.age   = age
		self.sex   = sex
		
class customer(person):
	def __init__(self, name, age, sex, balence):
	
		person.__init__(self, name, age, sex)
		
		self.balence = balence
		
	def deposit(self, amount):
		self.balence += amount
	
	def withdraw(self, amount):
		self.balence -= amount
	
	def info(self):
		print(self.name)
		print(self.age)
		print(self.sex)
		print(self.balence)
		
John = customer("John", 22, "Male", 22000)
Jane = customer("Jane", 53, "Female", 500)

John.deposit(1000)
Jane.withdraw(500)

John.info()
Jane.info()