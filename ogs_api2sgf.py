# Doesn't handle handicap games or games with setup.

import requests

# -------------------------------------------------------------------------------------------------

def make_root(o):

	root = ";"

	try:
		pb = o["players"]["black"]["username"]
		root += f"PB[{pb}]"
	except:
		pass

	try:
		pw = o["players"]["white"]["username"]
		root += f"PW[{pw}]"
	except:
		pass

	try:
		ru = o["rules"]
		root += f"RU[{ru}]"
	except:
		pass

	try:
		km = o["komi"]
		root += f"KM[{km}]"
	except:
		pass

	return root

# -------------------------------------------------------------------------------------------------

def make_move_nodes(o):
	move_string_elements = []
	colour = "B"
	for move in o["gamedata"]["moves"]:
		sgf = chr(move[0] + 97) + chr(move[1] + 97)
		node = f";{colour}[{sgf}]"
		move_string_elements.append(node)
		colour = "B" if colour == "W" else "W"
	return "".join(move_string_elements)

# -------------------------------------------------------------------------------------------------

game_id = input("OGS game ID? ")
url = f"https://online-go.com/api/v1/games/{game_id}"
j = requests.get(url).json()

print("(" + make_root(j) + make_move_nodes(j) + ")")

