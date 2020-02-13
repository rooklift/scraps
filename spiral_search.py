def nearest_xy_spiral_search(self, x, y):

	# Return the nearest x, y that isn't in use in self.foo.
	# Spiral search pattern.

	d = 0	# Direction. 0 = down, 1 = right, 2 = up, 3 = left
	v = 1	# Steps remaining in this direction.
	m = 1	# Length of an edge in the spiral.

	while 1:

		if x >= 0 and x < self.width and y >= 0 and y < self.height:
			if self.foo[x][y] is None:
				return x, y

		if d == 0:
			y += 1
		elif d == 1:
			x += 1
		elif d == 2:
			y -= 1
		elif d == 3:
			x -= 1

		v -= 1

		if v == 0:

			d += 1
			if d > 3:
				d = 0

			v = m

			if d == 0 or d == 2:
				v += 1
				m += 1
