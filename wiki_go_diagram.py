import copy, itertools, sys
import gofish


get_next_terminator = itertools.count(start = 99, step = 100)


def print_diagram(array):

	print('{{Goban')

	for y in range(1, len(array)):
		for x in range(1, len(array)):
			print("|{}".format(array[x][y]), end="")
		print()

	print('|20}}')


def add_move_to_array(node, array):
	try:
		x, y = node.what_was_the_move()
	except:
		return

	val = str(node.moves_made % 100)
	if val == "0":
		val = "00"
	if len(val) == 1:
		val = char_from_colour(node.move_colour()) + val
	array[x][y] = val


def char_from_colour(colour, pad = False):

	extra = " " if pad else ""

	if colour == gofish.BLACK:
		return "b" + extra
	if colour == gofish.WHITE:
		return "w" + extra
	if colour == gofish.EMPTY:
		return " " + extra

	return "?" + extra


def get_and_convert_board(node):

	# Given a board.state, convert it into so that it has the values Wikipedia {{Goban}} expects.

	array = copy.deepcopy(node.board.state)

	for i in range(len(array)):
		for j in range(len(array)):
			array[i][j] = char_from_colour(array[i][j], True)

	return array


def main():

	node = gofish.load(sys.argv[1])
	next_terminator = get_next_terminator.__next__()

	array = get_and_convert_board(node)

	# The root might have a move, deal with it if it exists...
	add_move_to_array(node, array)

	while 1:

		if len(node.children) == 0:
			print_diagram(array)
			break
		else:
			node = node.children[0]

		if node.moves_made > next_terminator:

			next_terminator = get_next_terminator.__next__()
			print_diagram(array)

			array = get_and_convert_board(node)

		add_move_to_array(node, array)


if __name__ == "__main__":
	main()
	input()

