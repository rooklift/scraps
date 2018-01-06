import os, requests, subprocess

LIMIT = 30
MY_ID = 4355	# Not really
CHLORINE_DIR = "C:\\Users\\Owner\\Desktop\\chlorine"

rank_lookup = {1: "1   ", 2: " 2  ", 3: "  3 ", 4: "   4"}

class RecentGames:

	def __init__(self):

		self.game_ids = []
		self.reload()

	def reload(self):

		recent = reversed(requests.get("http://api.halite.io/v1/api/user/{}/match?&order_by=desc,time_played&limit={}".format(MY_ID, LIMIT)).json())

		for game in recent:

			if game["game_id"] not in self.game_ids:

				self.game_ids.append(game["game_id"])

				my_rank = " ?? "

				players_dict = game["players"]
				players = []

				for pid, player in players_dict.items():
					players.append(player)
					if int(pid) == MY_ID:
						my_rank = rank_lookup[player["rank"]]

				players = sorted(players, key = lambda x : x["rank"])

				usernames_list = []
				for player in players:
					username = "{0:<16}".format(player["username"])
					usernames_list.append(username)

				usernames = " ".join(usernames_list)

				challenge_string = "<-- ch" if game["challenge_id"] is not None else ""

				print(" {0:>3} ({1:>4}s, {2:>3}t,  {3}x{4}) {5} {6}   {7}".format(
					len(self.game_ids) - 1, game["ships_produced"], game["turns_total"], game["map_width"], game["map_height"], my_rank, usernames, challenge_string))

	def get_game_id(self, n):

		return self.game_ids[n]

	def current_len(self):

		return len(self.game_ids)


def load_in_chlorine(filename):
	subprocess.Popen("electron \"{}\" -o \"{}\"".format(CHLORINE_DIR, filename), shell = True)


rg = RecentGames()

while 1:

	s = input("> ")

	if len(s) > 0 and s in "rR":
		rg.reload()
		continue

	n = int(s)
	if n < 0 or n >= rg.current_len():
		continue

	game_id = rg.get_game_id(n)

	local_filename = "{}.hlt".format(game_id)

	if not os.path.exists(local_filename):
		url = "https://api.halite.io/v1/api/user/{}/match/{}/replay".format(MY_ID, game_id)
		hlt = requests.get(url)
		with open(local_filename, "wb") as output:
			output.write(hlt.content)

	load_in_chlorine(os.path.abspath(local_filename))
