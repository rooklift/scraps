import json, requests, sys

speed_comments = False

# -------------------------------------------------------------------------------------------------

def result_string(o):
	try:
		b_score = o["gamedata"]["score"]["black"]["total"]
		w_score = o["gamedata"]["score"]["white"]["total"]
		if type(b_score) in [int, float] and type(w_score) in [int, float]:
			if b_score > w_score:
				return "B+{}".format(b_score - w_score)
			elif w_score > b_score:
				return "W+{}".format(w_score - b_score)
	except:
		pass

	try:
		if o["white_lost"] and not o["black_lost"]:
			if o["outcome"] == "Resignation":
				return "B+R"
			else:
				return "B+"
		elif o["black_lost"] and not o["white_lost"]:
			if o["outcome"] == "Resignation":
				return "W+R"
			else:
				return "W+"
	except:
		pass

	return ""

# -------------------------------------------------------------------------------------------------

def make_root(o):

	access = {	# lambdas, because many of these could throw with KeyError or somesuch...
		"CA": lambda : "UTF-8",
		"GM": lambda : 1,
		"FF": lambda : 4,
		"PB": lambda : o["players"]["black"]["username"],
		"PW": lambda : o["players"]["white"]["username"],
		"SZ": lambda : o["width"] if o["width"] == o["height"] else "{}:{}".format(o["width"], o["height"]),
		"RU": lambda : o["rules"],
		"KM": lambda : o["komi"],
		"GN": lambda : o["gamedata"]["game_name"],
		"DT": lambda : o["started"].split("T")[0],
		"RE": lambda : result_string(o),
	}

	root = ";"

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

		if speed_comments:
			ms = int(move[2])
			comment = "C[{:.2f} s]".format(ms / 1000)
		else:
			comment = ""

		node = ";{}[{}]{}".format(colour, coord, comment)
		move_string_elements.append(node)

		if not o["gamedata"]["free_handicap_placement"] or len(move_string_elements) >= o["handicap"]:
			colour = "B" if colour == "W" else "W"

	return "".join(move_string_elements)

# -------------------------------------------------------------------------------------------------

if len(sys.argv) > 1:
	game_id = sys.argv[-1]
else:
	game_id = input("OGS game ID? ")

if "/game/" in game_id:			# e.g. https://online-go.com/game/123456
	game_id = game_id.split("/game/")[1]

url = "https://online-go.com/api/v1/games/{}".format(game_id)
j = requests.get(url).json()

print()
if "error" in j:
	print(j["error"])
else:
	print("(" + make_root(j) + make_move_nodes(j) + ")")
print()
