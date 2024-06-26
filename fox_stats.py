import os
import gofish2 as gf

directories = ["Fox"]
report_count = 4

class Player:
	def __init__(self, name):
		self.name = name
		self.wins = dict()		# opponent rank as string --> count
		self.losses = dict()	# opponent rank as string --> count

	def add_win_vs(self, opp_rank):
		if opp_rank in self.wins:
			self.wins[opp_rank] += 1
		else:
			self.wins[opp_rank] = 1

	def add_loss_vs(self, opp_rank):
		if opp_rank in self.losses:
			self.losses[opp_rank] += 1
		else:
			self.losses[opp_rank] = 1

	def print_stats(self):
		print()
		print(" {} ({})".format(self.name, self.count_games()))
		print()
		keys = set(self.wins.keys()).union(set(self.losses.keys()))
		keys = sorted(list(keys), key = lambda x: rank_value(x), reverse = True)
		for key in keys:
			print("   {}: {}-{}".format(key, self.wins.get(key, 0), self.losses.get(key, 0)))

	def count_games(self):
		return sum(self.wins.values()) + sum(self.losses.values())


def rank_value(s):
	try:
		if len(s) == 0:
			return -100
		elif "D" in s:
			return int(s[0])
		elif "k" in s:
			return int(s[0]) * -1
		else:
			return -101
	except:
		return -102

def main():

	os.chdir(os.path.dirname(os.path.realpath(__file__)))

	players = dict()		# name --> player object

	for directory in directories:

		files = os.listdir(directory)

		for file in files:

			if not file.lower().endswith(".sgf"):
				continue

			root = gf.load(os.path.join(directory, file))[0]

			if "B+" in root.get("RE"):
				winner = "B"
			elif "W+" in root.get("RE"):
				winner = "W"
			else:
				continue

			PB = root.get("PB")
			PW = root.get("PW")

			for name in [PB, PW]:
				if name not in players:
					players[name] = Player(name)

			BR = root.get("BR").replace("级", "k").replace("段", "D") or "??"
			WR = root.get("WR").replace("级", "k").replace("段", "D") or "??"

			if winner == "B":
				players[PB].add_win_vs(WR)
				players[PW].add_loss_vs(BR)
			else:
				players[PB].add_loss_vs(WR)
				players[PW].add_win_vs(BR)

	interesting = sorted(list(players.values()), key = lambda x: [x.count_games() * -1, x.name])
	interesting = interesting[0:report_count]

	for player in interesting:
		player.print_stats()

	print()
	print(" TOTAL: {}".format(sum([player.count_games() for player in interesting])))




main()
input()
