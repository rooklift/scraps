import json, sys

with open(sys.argv[1], encoding="utf8") as infile:
	raw = infile.read()

cards = dict()

cardname = ""
card = dict()

n = 0

for line in raw.split("\n"):

	n += 1

	line = line.strip()

	if line.endswith(","):
		line = line[0:-1]

	if line.startswith("[") and line.endswith("] = {"):
		cardname = line[2:-6]
	elif line.startswith("Cost"):
		card["cost"] = int(line.split("=")[1])
	elif line.startswith("Type"):
		card["type"] = line.split("=")[1].strip().replace("\"", "")
	elif line.startswith("Text"):
		card["text"] = line.split("=")[1].strip().replace("\"", "").replace("<br>", " ").replace("“", "'").replace("”", "'")

	if cardname and len(card) == 3:
		cards[cardname] = card
		cardname = ""
		card = dict()

with open(sys.argv[1][0:-3] + "json", "w") as outfile:
	outfile.write(json.dumps(cards, indent = 4))

