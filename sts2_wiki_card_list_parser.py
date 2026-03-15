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
		raw = infile.read().strip()

	all_lines = raw.split("\n")

	cards = dict()

	card_name = ""
	card = None
	cost_plus = None

	for n, line in enumerate(all_lines):

		line = line.strip()

		if line.startswith("[") and line.endswith("] = {"):
			if card_name or card or cost_plus:
				raise ValueError
			card_name = line[2:-6]
			card = dict()
		elif line.startswith("Cost ="):
			card["cost"] = "X" if extract_value(line) == "-1" else "?" if extract_value(line) == "-2" else extract_value(line)
		elif line.startswith("CostPlus ="):
			cost_plus = extract_value(line)
		elif line.startswith("Type ="):
			card["type"] = extract_value(line)
		elif line.startswith("Text ="):
			card["text"] = extract_value(line)
		elif line == "}" or line == "},":
			if card_name and len(card) == 3:
				if cost_plus:
					card["cost"] = "[" + card["cost"] + "|" + cost_plus + "]"
				cards[card_name] = card
				card_name = ""
				card = None
				cost_plus = None
			elif n == len(all_lines) - 1:
				break
			else:
				raise ValueError

	with open(filename[0:filename.rindex(".")] + ".json", "w") as outfile:
		outfile.write(json.dumps(cards, indent = 4))

