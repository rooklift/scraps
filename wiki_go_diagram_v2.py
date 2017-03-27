
# Assumptions:
#	- No moves in root
#	- No handicap
#	- No fruity ordering (e.g. two black moves in a row)


import copy, sys
import gofish


class Move():
	def __init__(self, colour, number, x, y):
		assert(colour in ["b", "w"])
		self.colour = colour
		self.number = number
		self.x = x
		self.y = y

	def representation(self):
		val = self.number % 100
		if val == 0:
			return "00"
		if val < 10:
			return self.colour + str(val)
		return str(val)


class Record():

	def __init__(self, size = 19):
		self.size = size
		self.array = [[[] for x in range(self.size + 1)] for y in range(self.size + 1)]
		self.total_adds = 0

	def add(self, node):
		self.total_adds += 1
		move = node.what_was_the_move()
		if move == None:
			return
		x, y = move
		colour = "b" if node.move_colour() == gofish.BLACK else "w"

		move = Move(colour, self.total_adds, x, y)
		self.array[x][y].append(move)

	def print(self):
		self.warnings = []

		self.print_part(1, 99)

		for n in range(100, self.total_adds + 1, 100):
			self.print_part(n, n + 99)

		print("\n".join(self.warnings))

	def print_part(self, start, end):
		ascii_array = [["  " for x in range(self.size + 1)] for y in range(self.size + 1)]

		for x in range(self.size + 1):
			for y in range(self.size + 1):
				for move in self.array[x][y]:
					if move.number <= end:
						if move.number < start:
							ascii_array[x][y] = move.colour + " "
						else:
							if ascii_array[x][y] == "  ":
								ascii_array[x][y] = move.representation()
							else:
								self.warnings.append("{} at {}".format(move.number, self.array[x][y][0].number))

		print("{{Goban")
		for y in range(1, len(ascii_array)):
			for x in range(1, len(ascii_array)):
				print("|{}".format(ascii_array[x][y]), end="")
			print()
		print("|20}}")
		print()


def main():

	node = gofish.load(sys.argv[1])

	record = Record(int(node.get_value("SZ")))

	# Note that we assume no moves in the root.

	while 1:

		if len(node.children) == 0:
			break
		else:
			node = node.children[0]

		record.add(node)

	record.print()


if __name__ == "__main__":
	main()
	input()

