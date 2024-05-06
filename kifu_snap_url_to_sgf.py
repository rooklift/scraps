url = "https://www.crazy-sensei.com/?lang=en&location=kifu_snap&board_size=19&position=...%23O....OO%23.%23OO.....%23%23OO.O.O%23%23.%23%23OO....%23OO%23OO.OO%23...%23O..%23.%23O%23%23O%23..O%23%23..%23O..O%23%23%23%23OO..O%23....%23%23O.OOO%23.%23%23O.O%23%23%23.%23OO....O%23%23..%23OO%23O%23.%23%23OO.O%23OO%23..%23%23OOOO%23%23O%23...O%23%23...%23O..O%23%23%23OOOOO.O%23%23%23.%23O..O%23%23OOO%23O..O%23O%23%23OO.OO%23%23%23%23%23%23%23OOOOO%23.%23OO%23OOOO%23OO.O%23%23%23O%23..%23%23%23%23%23O.O%23%23O%23.%23OOO%23%23.%23.%23O%23.O%23%23..%23.%23%23%23O%23%23%23%23OO..OO%23....%23O%23O%23O%23OO...O%23%23..%23.%23OOOOOO%23..OO%23.%23...%23OO.O.......O%23.%23..%23OO.........O%23%23%23..&color=b&rules=c&komi=7.5&handicap=0#analysis"

data = url.split("position=")[1].split("&")[0].replace("%23", "X")		# %23 is actually hex code for #, but whatever.

alpha = "abcdefghijklmnopqrstuvwxyz"

AB = []
AW = []

def i_to_sgf(i):
	x = i % 19
	y = i // 19
	return alpha[x] + alpha[y]

for i in range(361):
	c = data[i]
	if c == "O":
		AW.append(i_to_sgf(i))
	if c == "X":
		AB.append(i_to_sgf(i))

print("(;AB[", end="")
print("][".join(AB), end="")
print("]AW[", end="")
print("][".join(AW), end="")
print("])")
