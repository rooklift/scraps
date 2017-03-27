
# Assumptions:
#	- No moves in root
#	- No handicap
#	- No fruity ordering (e.g. two black moves in a row)


import copy, sys
import gofish


class Warning():
	def __init__(self, new, old):
		self.new = new
		self.old = old

	def __lt__(self, other):
		if self.new < other.new:
			return True
		else:
			return False

	def __str__(self):
		return "{} at {}".format(self.new, self.old)


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

	def __init__(self, root):

		self.size = int(root.get_value("SZ"))
		self.total_adds = 0

		self.moves = [[[] for x in range(self.size + 1)] for y in range(self.size + 1)]
		self.positions = dict()

		node = root

		while 1:
			self.add(node)
			if len(node.children) == 0:
				break
			else:
				node = node.children[0]

	def add(self, node):
		self.add_move(node)
		self.add_position(node)
		self.total_adds += 1

	def add_move(self, node):
		move = node.what_was_the_move()
		if move == None:
			return
		x, y = move
		colour = "b" if node.move_colour() == gofish.BLACK else "w"

		move = Move(colour, node.moves_made, x, y)
		self.moves[x][y].append(move)

	def add_position(self, node):
		ascii_array = [["  " for x in range(self.size + 1)] for y in range(self.size + 1)]

		for x in range(self.size + 1):
			for y in range(self.size + 1):
				s = "  "
				if node.board.state[x][y] == gofish.BLACK:
					s = "b "
				if node.board.state[x][y] == gofish.WHITE:
					s = "w "
				ascii_array[x][y] = s

		self.positions[node.moves_made] = ascii_array

	def print(self):
		self.print_part(1, 99)
		for n in range(100, self.total_adds + 1, 100):
			self.print_part(n, n + 99)

	def print_part(self, start, end):

		# The following can fail if start is 1 and there is no position recorded for 0 moves made
		# because the root contained a move...

		try:
			ascii_array = copy.deepcopy(self.positions[start - 1])
		except KeyError:
			ascii_array = [["  " for x in range(self.size + 1)] for y in range(self.size + 1)]

		warnings = []

		for x in range(self.size + 1):
			for y in range(self.size + 1):
				for move in self.moves[x][y]:
					if start <= move.number <= end:
						if ascii_array[x][y] == "  ":
							ascii_array[x][y] = move.representation()
						else:
							warnings.append(Warning(move.number, self.moves[x][y][0].number))

		print()
		print("{{Goban")
		for y in range(1, len(ascii_array)):
			for x in range(1, len(ascii_array)):
				print("|{}".format(ascii_array[x][y]), end="")
			print()
		print("|20}}")

		if warnings:
			print()
			for w in sorted(warnings):
				print(w)


def main():
	root = gofish.load(sys.argv[1])
	record = Record(root)
	record.print()


if __name__ == "__main__":
	main()
	input()

