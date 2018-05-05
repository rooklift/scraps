#!/usr/bin/env python3

import subprocess
import gofish

LOGFILE = "autogtp.log"

def point_from_english_string(s):	# "Q16"     --->    16, 4
	if s == "pass":
		return None
	s = s.upper()
	x = "!ABCDEFGHJKLMNOPQRSTUVWXYZ".index(s[0])
	y = 19 - int(s[1:]) + 1
	return x, y

def string_from_point(x, y):		# 16, 4     --->    "pd"
	s = ""
	s += chr(x + 96)
	s += chr(y + 96)
	return s

def string_from_english_string(s):
	point = point_from_english_string(s)
	if point == None:
		return ""
	return string_from_point(*point)


raw = subprocess.check_output(["tail", "-n", "1", LOGFILE]).decode("ascii")
tokens = raw.replace("(", "").replace(")", "").split()
moves = [[tokens[n], tokens[n + 1], tokens[n + 2]] for n in range(0, len(tokens), 3)]
output = "(;CA[UTF-8]FF[4]GM[1]SZ[19]"
for move in moves:
	s = string_from_english_string(move[2])
	output += ";{}[{}]".format(move[1], s)
output += ")"

node = gofish.parse_sgf(output)
while len(node.children) > 0:
	node = node.children[0]
node.board.dump()

