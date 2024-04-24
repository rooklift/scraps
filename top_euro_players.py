# Download alleuro_lp from:
# https://www.europeangodatabase.eu/EGD/EGF_rating_system.php

def get_lines(filename):
	with open(filename, "rb") as f:
		raw = f.read().decode("utf8")
	return [line.strip() for line in raw.split("\n") if line.strip() != ""]

class Player:
	def __init__(self, line):
		tokens = line.split()
		if tokens[-1] == "0":
			tokens.append("none")
		self.last_tourn = tokens[-1]
		self.tourns_attended = int(tokens[-2])
		self.elo = int(tokens[-3])
		self.p_and_d = tokens[-4]
		self.grade = tokens[-5]
		self.club = tokens[-6]
		self.country = tokens[-7]
		self.id = int(tokens[0])
		self.name = " ".join(tokens[1:len(tokens) - 7])

def main():
	lines = get_lines("list.txt")
	players = []
	for line in lines:
		players.append(Player(line))
	players.sort(key = lambda x : x.elo, reverse = True)
	for player in players[:100]:
		print("{:30}  {}  {}  {}".format(player.name, player.country, player.grade, player.elo))



main()
input()
