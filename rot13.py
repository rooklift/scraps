import sys

rot_lower = "nopqrstuvwxyzabcdefghijklm"
rot_upper = "NOPQRSTUVWXYZABCDEFGHIJKLM"

def is_lowercase_char(c):	# specifically in the ASCII range
	return isinstance(c, str) and (len(c) == 1) and c >= "a" and c <= "z"

def is_uppercase_char(c):	# specifically in the ASCII range
	return isinstance(c, str) and (len(c) == 1) and c >= "A" and c <= "Z"

def rot13(s):
	chars = []
	for c in s:
		if is_lowercase_char(c):
			i = ord(c) - 97
			chars.append(rot_lower[i])
		elif is_uppercase_char(c):
			i = ord(c) - 65
			chars.append(rot_upper[i])
		else:
			chars.append(c)
	return "".join(chars)

with open(sys.argv[-1], encoding="utf8") as infile:
	for line in infile:
		print(rot13(line), end="")
