import json, sys

def extract_value(s):
	s = s.split("=")[1].strip()
	if s.endswith(","):				# This...
		s = s[:-1]
	if s.endswith("\""):			# ...before this
		s = s[:-1]
	if s.startswith("\""):
		s = s[1:]
	s = s.replace("<br>", " ").replace("“", "'").replace("”", "'")
	return s

for filename in sys.argv[1:]:

	with open(filename, encoding="utf8") as infile:
		raw = infile.read()

	cards = dict()

	cardname = ""
	card = None

	for line in raw.split("\n"):

		line = line.strip()

		if line.startswith("[") and line.endswith("] = {"):
			if cardname or card:
				raise ValueError
			cardname = line[2:-6]
			card = dict()
		elif line.startswith("Cost ="):
			card["cost"] = "X" if extract_value(line) == "-1" else extract_value(line)
		elif line.startswith("CostPlus ="):
			card["cost"] = "[" + card["cost"] + "|" + extract_value(line) + "]"		# Assumes CostPlus line comes after Cost (but will throw if not)
		elif line.startswith("Type ="):
			card["type"] = extract_value(line)
		elif line.startswith("Text ="):
			card["text"] = extract_value(line)

		if cardname and len(card) == 3:
			cards[cardname] = card
			cardname = ""
			card = None

	with open(filename[0:filename.rindex(".")] + ".json", "w") as outfile:
		outfile.write(json.dumps(cards, indent = 4))

