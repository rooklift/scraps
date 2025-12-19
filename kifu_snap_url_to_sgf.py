url = input("Paste url:\n")

data = url.split("position=")[1].split("&")[0].replace("%23", "X")		# %23 is actually hex code for #, but whatever.

alpha = "abcdefghijklmnopqrstuvwxyz"

BOARD_SIZE = 19

for n in range(5, 26):
	if f"board_size={n}" in url:
		BOARD_SIZE = n

AB = []
AW = []

def i_to_sgf(i):
	x = i % BOARD_SIZE
	y = i // BOARD_SIZE
	return alpha[x] + alpha[y]

for i in range(BOARD_SIZE * BOARD_SIZE):
	c = data[i]
	if c == "O":
		AW.append(i_to_sgf(i))
	if c == "X":
		AB.append(i_to_sgf(i))

print("(;SZ[" + str(BOARD_SIZE) + "]AB[", end="")
print("][".join(AB), end="")
print("]AW[", end="")
print("][".join(AW), end="")
print("])")

input()
