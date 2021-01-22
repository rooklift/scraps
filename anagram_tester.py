class NegativeResult(Exception):
	pass

original = "what ever"

original_dict = dict()

for c in original:
	c = c.lower()
	if not c.isspace():
		if c not in original_dict:
			original_dict[c] = 1
		else:
			original_dict[c] += 1

while 1:
	try:
		t = input("> ")
		new_dict = dict(original_dict)
		for c in t:
			c = c.lower()
			if not c.isspace():
				if c not in new_dict:
					raise NegativeResult
				else:
					new_dict[c] -= 1
		for c in new_dict:
			if new_dict[c] != 0:
				raise NegativeResult
		print("Yes")
	except NegativeResult:
		print("No")

