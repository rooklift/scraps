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

	# Each item in the self.moves list is itself an array of moves for that spot.
	# Each item in the self.positions dict is a 2D array of strings representing the board after n moves (where n is the key).

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

		highest_move_shown = 0

		for x in range(self.size + 1):
			for y in range(self.size + 1):
				for move in self.moves[x][y]:
					if start <= move.number <= end:
						if move.number > highest_move_shown:
							highest_move_shown = move.number
						if ascii_array[x][y] == "  ":
							ascii_array[x][y] = move.representation()
						else:
							warnings.append(Warning(move.number, self.moves[x][y][0].number))

		warnings = sorted(warnings)
		str_warnings = list(map(str, warnings))

		if len(str_warnings) == 0:
			warn_string = ""
		else:
			warn_string = "(" + ", ".join(str_warnings) + ")"

		print()
		print('{| style="display:inline; display:inline-table;"')
		print('| style="border: solid thin; padding: 2px;" |')
		print('{{Goban')
		for y in range(1, len(ascii_array)):
			for x in range(1, len(ascii_array)):
				print("|{}".format(ascii_array[x][y]), end="")
			print()
		print('|20}}')
		print('|-')
		print('| style="text-align:center" | Moves {} to {} {}'.format(start, highest_move_shown, warn_string))
		print('|}')


def main():
	root = gofish.load(sys.argv[1])
	record = Record(root)
	record.print()


if __name__ == "__main__":
	main()
	input()

