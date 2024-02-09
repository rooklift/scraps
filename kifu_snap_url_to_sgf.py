data = ".....OX.......OOX......OOXXOXXOXOXX.......OX..X..XXOX.X.....OOXX...XXO.OXXX.....OOXXXXXXXXOOXO...OOOXXXOOXOOXXOOO.OOOXOXXO.OOO.OOXOOX.XXXXXO.O..O..OXXOOXXOO.XO..O..O..OXXX.XXOOO.OO..OO.OOXXXXOOX...O.OOX.OOXXOXXXO..OOXXXXXXXXXOOOXO.....OXXOOOXXXOX.XOO....OX...XOOOOX.XOO....OXX..XXXOX...XXO...OXXO..XO.O....XOOX.OXOXXXOO.O...XXXO..OOOOXOOO.O...XOOO....OXXXXXO..."

# Note the actual URL may use %23 for some reason

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
