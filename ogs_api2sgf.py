# Doesn't handle handicap games or games with setup.

import requests

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

	return root

# -------------------------------------------------------------------------------------------------

def make_move_nodes(o):
	move_string_elements = []
	colour = "B"
	for move in o["gamedata"]["moves"]:
		if move[0] < 0 or move[1] < 0:
			coord = ""
		else:
			coord = chr(move[0] + 97) + chr(move[1] + 97)
		node = ";{}[{}]".format(colour, coord)
		move_string_elements.append(node)
		colour = "B" if colour == "W" else "W"
	return "".join(move_string_elements)

# -------------------------------------------------------------------------------------------------

game_id = input("OGS game ID? ")
url = "https://online-go.com/api/v1/games/{}".format(game_id)
j = requests.get(url).json()

print()
print("(" + make_root(j) + make_move_nodes(j) + ")")
input()
