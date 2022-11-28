import requests, sys

# -------------------------------------------------------------------------------------------------

def make_root(o):

	access = {
		"PB": lambda : o["players"]["black"]["username"],
		"PW": lambda : o["players"]["white"]["username"],
		"SZ": lambda : o["width"] if o["width"] == o["height"] else "{}:{}".format(o["width"], o["height"]),
		"RU": lambda : o["rules"],
		"KM": lambda : o["komi"],
		"GN": lambda : o["gamedata"]["game_name"],
		"DT": lambda : o["started"].split("T")[0],
	}

	root = ";CA[UTF-8]GM[1]FF[4]"

	for sgf_key, fn in access.items():
		try:
			root += "{}[{}]".format(sgf_key, fn())
		except:
			pass

	if o["gamedata"]["initial_state"]["black"]:
		s = o["gamedata"]["initial_state"]["black"]
		coords = [s[i : i + 2] for i in range(0, len(s), 2)]
		root += "AB[{}]".format("][".join(coords))

	if o["gamedata"]["initial_state"]["white"]:
		s = o["gamedata"]["initial_state"]["white"]
		coords = [s[i : i + 2] for i in range(0, len(s), 2)]
		root += "AW[{}]".format("][".join(coords))

	return root

# -------------------------------------------------------------------------------------------------

def make_move_nodes(o):

	move_string_elements = []

	colour = o["gamedata"]["initial_player"][0].upper()
	if colour not in ["B", "W"]:
		raise ValueError

	for move in o["gamedata"]["moves"]:

		if move[0] < 0 or move[1] < 0:
			coord = ""
		else:
			coord = chr(move[0] + 97) + chr(move[1] + 97)

		node = ";{}[{}]".format(colour, coord)
		move_string_elements.append(node)

		if not o["gamedata"]["free_handicap_placement"] or len(move_string_elements) >= o["handicap"]:
			colour = "B" if colour == "W" else "W"

	return "".join(move_string_elements)

# -------------------------------------------------------------------------------------------------

if len(sys.argv) > 1:
	game_id = sys.argv[-1]
else:
	game_id = input("OGS game ID? ")

url = "https://online-go.com/api/v1/games/{}".format(game_id)
j = requests.get(url).json()

print()
print("(" + make_root(j) + make_move_nodes(j) + ")")
input()
