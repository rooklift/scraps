import random, sys, tkinter

WIDTH = 10
HEIGHT = 20

BLOCKSIZE = 32
BLOCKMARGIN = 2

GRAVITY_TICK = 10

rotate_right_5x5 = {
	(-2,-2) : [4,0],	(-1,-2) : [3,1],	(0,-2) : [2,2],		(1,-2) : [1,3],		(2,-2) : [0,4],
	(-2,-1) : [3,-1],	(-1,-1) : [2,0],	(0,-1) : [1,1],		(1,-1) : [0,2],		(2,-1) : [-1,3],
	(-2,0)  : [2,-2],	(-1,0)  : [1,-1],	(0,0)  : [0,0],		(1,0)  : [-1, 1],	(2,0)  : [-2,2],
	(-2,1)  : [1,-3],	(-1,1)  : [0,-2],	(0,1)  : [-1, -1],	(1,1)  : [-2, 0],	(2,1)  : [-3,1],
	(-2,2)  : [0,-4],	(-1,2)  : [-1,-3],	(0,2)  : [-2, -2],	(1,2)  : [-3,-1],	(2,2)  : [-4,0]
}

rotate_left_5x5 = {
	(-2,-2) : [0,4],	(-1,-2) : [-1,3],	(0,-2) : [-2,2],	(1,-2) : [-3,1],	(2,-2) : [-4,0],
	(-2,-1) : [1,3],	(-1,-1) : [0,2],	(0,-1) : [-1,1],	(1,-1) : [-2,0],	(2,-1) : [-3,-1],
	(-2,0)  : [2,2],	(-1,0)  : [1,1],	(0,0)  : [0,0],		(1,0)  : [-1, -1],	(2,0)  : [-2,-2],
	(-2,1)  : [3,1],	(-1,1)  : [2, 0],	(0,1)  : [1, -1],	(1,1)  : [0, -2],	(2,1)  : [-1,3],
	(-2,2)  : [4,0],	(-1,2)  : [3,-1],	(0,2)  : [2, -2],	(1,2)  : [1,-3],	(2,2)  : [0,-4]
}

class GameOver(Exception): pass
class BlockLock(Exception): pass

world = [[None for y in range(HEIGHT)] for x in range(WIDTH)]

class Block:
	def __init__(self, x, y, colour):
		self.x = x
		self.y = y
		self.colour = colour

	def canmove(self, dx, dy):
		if self.x + dx < 0 or self.x + dx >= WIDTH:
			return False
		if self.y + dy >= HEIGHT:
			return False
		if self.y + dy < 0:
			return True								# Note that pieces going < 0 height is allowed
		if world[self.x + dx][self.y + dy]:
			return False
		return True

	def move(self, dx, dy):
		self.x += dx
		self.y += dy

	def lock(self):
		if self.x >= 0 and self.x < WIDTH and self.y >= 0 and self.y < HEIGHT:			# Only the self.y >= 0 test should ever fail
			world[self.x][self.y] = self

class Piece:
	def __init__(self, coords, colour):
		self.blocks = []
		for coord in coords:
			self.blocks.append(Block(coord[0], coord[1], colour))
		for block in self.blocks:
			if world[block.x][block.y]:
				self.lock()
				raise GameOver
		self.midblock = None
		self.state = 0							# Might be used by pieces that only toggle through 2 states

	def rotate_right(self):
		raise NotImplementedError

	def rotate_left(self):
		raise NotImplementedError

	def canmove(self, dx, dy):
		canmove = True
		for block in self.blocks:
			if not block.canmove(dx, dy):
				canmove = False
				break
		return canmove

	def move(self, dx, dy):
		for block in self.blocks:
			block.move(dx, dy)

	def handle_move_command(self, dx, dy):
		if self.canmove(dx, dy):
			self.move(dx, dy)
		elif dx == 0 and dy == 1:				# User commanded a downwards move, which is allowed to trigger a lock
			raise BlockLock

	def handle_gravity(self):
		if self.canmove(0, 1):
			self.move(0, 1)
		else:
			raise BlockLock

	def rotate_right_standard(self):
		canrotate = True
		for block in self.blocks:
			if block is not self.midblock:
				i = block.x - self.midblock.x
				j = block.y - self.midblock.y
				dx, dy = rotate_right_5x5[(i,j)]
				if not block.canmove(dx, dy):
					canrotate = False
		if canrotate:
			for block in self.blocks:
				if block is not self.midblock:
					i = block.x - self.midblock.x
					j = block.y - self.midblock.y
					dx, dy = rotate_right_5x5[(i,j)]
					block.move(dx, dy)

	def rotate_left_standard(self):
		canrotate = True
		for block in self.blocks:
			if block is not self.midblock:
				i = block.x - self.midblock.x
				j = block.y - self.midblock.y
				dx, dy = rotate_left_5x5[(i,j)]
				if not block.canmove(dx, dy):
					canrotate = False
		if canrotate:
			for block in self.blocks:
				if block is not self.midblock:
					i = block.x - self.midblock.x
					j = block.y - self.midblock.y
					dx, dy = rotate_left_5x5[(i,j)]
					block.move(dx, dy)

	def toggle_state(self):		# Could be used by the pieces that are 180 degree rotationally symmetric
		if self.state:
			self.rotate_right_standard()
			self.state = 0
		else:
			self.rotate_left_standard()
			self.state = 1

	def lock(self):
		for block in self.blocks:
			block.lock()

class Square(Piece):
	def __init__(self):
		Piece.__init__(self, [[WIDTH // 2 - 1, 0], [WIDTH // 2, 0], [WIDTH // 2 - 1, 1], [WIDTH // 2, 1]], "#808000")
	def rotate_right(self):
		pass
	def rotate_left(self):
		pass

class Alpha(Piece):
	def __init__(self):
		Piece.__init__(self, [[WIDTH // 2, 0], [WIDTH // 2, 1], [WIDTH // 2 - 1, 1], [WIDTH // 2 - 2, 1]], "#804000")
		self.midblock = self.blocks[2]
	def rotate_right(self):
		self.rotate_right_standard()
	def rotate_left(self):
		self.rotate_left_standard()

class Gamma(Piece):
	def __init__(self):
		Piece.__init__(self, [[WIDTH // 2 - 2, 0], [WIDTH // 2, 1], [WIDTH // 2 - 1, 1], [WIDTH // 2 - 2, 1]], "#004080")
		self.midblock = self.blocks[2]
	def rotate_right(self):
		self.rotate_right_standard()
	def rotate_left(self):
		self.rotate_left_standard()

class Tee(Piece):
	def __init__(self):
		Piece.__init__(self, [[WIDTH // 2 - 1, 0], [WIDTH // 2, 1], [WIDTH // 2 - 1, 1], [WIDTH // 2 - 2, 1]], "#800080")
		self.midblock = self.blocks[2]
	def rotate_right(self):
		self.rotate_right_standard()
	def rotate_left(self):
		self.rotate_left_standard()

class RightSnake(Piece):
	def __init__(self):
		Piece.__init__(self, [[WIDTH // 2 - 1, 0], [WIDTH // 2, 0], [WIDTH // 2 - 1, 1], [WIDTH // 2 - 2, 1]], "#008000")
		self.midblock = self.blocks[2]
	def rotate_right(self):
		self.rotate_right_standard()
	def rotate_left(self):
		self.rotate_left_standard()

class LeftSnake(Piece):
	def __init__(self):
		Piece.__init__(self, [[WIDTH // 2 - 1, 0], [WIDTH // 2 - 2, 0], [WIDTH // 2 - 1, 1], [WIDTH // 2, 1]], "#800000")
		self.midblock = self.blocks[2]
	def rotate_right(self):
		self.rotate_right_standard()
	def rotate_left(self):
		self.rotate_left_standard()

class Stick(Piece):
	def __init__(self):
		Piece.__init__(self, [[WIDTH // 2 - 2, 0], [WIDTH // 2 - 1, 0], [WIDTH // 2, 0], [WIDTH // 2 + 1, 0]], "#404080")
		self.midblock = self.blocks[2]
	def rotate_right(self):
		self.rotate_right_standard()
	def rotate_left(self):
		self.rotate_left_standard()

class Board(tkinter.Canvas):
	def __init__(self, owner, *args, **kwargs):
		tkinter.Canvas.__init__(self, owner, *args, **kwargs)
		self.owner = owner

		self.all_pieces = [Square, Alpha, Gamma, Tee, RightSnake, LeftSnake, Stick]

		self.keyboard = dict()
		self.score = 0
		self.tick = 0

		self.owner.wm_title("Tetris: 0")

		self.piece = random.choice(self.all_pieces)()
		self.iterate()

	def draw_block(self, block):
		left = block.x * BLOCKSIZE + BLOCKMARGIN
		top = block.y * BLOCKSIZE + BLOCKMARGIN
		self.create_rectangle(left, top, left + BLOCKSIZE - BLOCKMARGIN, top + BLOCKSIZE - BLOCKMARGIN, fill = block.colour)

	def draw_world(self, draw_piece = True):

		self.delete(tkinter.ALL)

		for x in range(WIDTH):
			for y in range(HEIGHT):
				block = world[x][y]
				if block:
					self.draw_block(block)

		if draw_piece:
			for block in self.piece.blocks:
				self.draw_block(block)

	def iterate(self):
		commanded_x = 0
		commanded_y = 0
		commanded_rotate = 0
		blocklockflag = False

		self.tick += 1

		if self.keyboard.get("a") or self.keyboard.get("left"):
			commanded_x -= 1

		if self.keyboard.get("d") or self.keyboard.get("right"):
			commanded_x += 1

		if self.keyboard.get("q") or self.keyboard.get("up"):
			commanded_rotate -= 1

		if self.keyboard.get("e") or self.keyboard.get("down"):
			commanded_rotate += 1

		if self.keyboard.get("space"):
			commanded_y += 1

		for k in ["a", "left", "d", "right", "q", "up", "e", "down"]:		# Don't clear "space"
			self.keyboard[k] = False

		if commanded_x:
			self.piece.handle_move_command(commanded_x, 0)

		if commanded_y:
			try:
				self.piece.handle_move_command(0, commanded_y)
			except BlockLock:
				blocklockflag = True

		if commanded_rotate > 0:
			self.piece.rotate_right()

		if commanded_rotate < 0:
			self.piece.rotate_left()

		if self.tick % GRAVITY_TICK == 0:
			try:
				self.piece.handle_gravity()
			except BlockLock:
				blocklockflag = True

		if blocklockflag:
			self.piece.lock()
			self.score += self.handle_clearances()
			self.owner.wm_title("Tetris: {}".format(self.score))
			try:
				self.piece = random.choice(self.all_pieces)()
			except GameOver:
				self.game_over()

		self.draw_world()
		self.after(40, self.iterate)

	def game_over(self):
		for y in range(HEIGHT - 1, -1, -1):
			for x in range(WIDTH):
				world[x][y] = Block(x, y, "#808080")
				self.draw_world(draw_piece = False)
				self.update_idletasks()
		sys.exit()

	def handle_clearances(self):
		lines_cleared = 0
		for y in range(HEIGHT):
			foundgap = 0
			for x in range(WIDTH):
				if not world[x][y]:
					foundgap = 1
					break
			if foundgap == 0:
				lines_cleared += 1
				for j in range(y, 0, -1):
					for i in range(WIDTH):
						world[i][j] = world[i][j - 1]
						if world[i][j]:						# Moved blocks will have wrong y coordinate set, fix this
							world[i][j].y = j
				# Clear the top row specially...
				for i in range(WIDTH):
						world[i][0] = None
		return lines_cleared

	def key_down(self, event):
		self.keyboard[event.keysym.lower()] = True

	def key_up(self, event):
		self.keyboard[event.keysym.lower()] = False

class Root(tkinter.Tk):
	def __init__(self, *args, **kwargs):

		tkinter.Tk.__init__(self, *args, **kwargs)
		self.resizable(width = False, height = False)
		self.protocol("WM_DELETE_WINDOW", self.quit)

		global board
		board = Board(self, width = WIDTH * BLOCKSIZE + BLOCKMARGIN, height = HEIGHT * BLOCKSIZE + BLOCKMARGIN,
					  background = "black", bd = 0, highlightthickness = 0)
		board.pack()

		self.bind("<Key>", board.key_down)
		self.bind("<KeyRelease>", board.key_up)


if __name__ == "__main__":
	app = Root()
	app.mainloop()
