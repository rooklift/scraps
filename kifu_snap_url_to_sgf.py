
alpha = "abcdefghijklmnopqrstuvwxyz"

data = data.replace("%23", "X")		# Note the actual URL may use %23 for some reason

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
