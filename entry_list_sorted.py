data = """
1	Smith, Jim	6k	Footown	FR
2	Jones, Joe	7k	Barville	UK
"""

lines = [line.strip() for line in data.split("\n") if len(line.strip()) > 0]

class Player:

	def __init__(self, num, name, rank, club, country):
		self.num = int(num)
		try:
			self.forename = name.split(",")[1].strip()
			self.surname = name.split(",")[0].strip()
		except:
			self.forename = name
			self.surname = name
		self.rank = rank
		self.club = club
		self.country = country

	def is_kyu(self):
		return self.rank.endswith("k")

	def is_dan(self):
		return self.rank.endswith("d")

	def is_rankless(self):
		return not self.is_kyu() and not self.is_dan()

	def fullname(self):
		return self.forename + " " + self.surname

	def dist_to_10d(self):
		if self.is_rankless():
			return 100
		else:
			numpart = int(self.rank[:-1])
			if self.is_dan():
				return 10 - numpart
			else:
				return 9 + numpart
			
	def __str__(self):
		return "\t{0: >4}  {1: <22} {2}".format(self.rank, self.fullname(), self.club)

	def __lt__(self, other):
		return self.dist_to_10d() < other.dist_to_10d()

players = []

for line in lines:
	num, name, rank, club, country = [token for token in line.split("\t") if token != ""]
	players.append(Player(num, name, rank, club, country))

print()
for item in sorted(players):
	print(item)
print()
input()

