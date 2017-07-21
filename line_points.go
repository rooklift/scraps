// Given 2 points, return a slice of points that need to be drawn
// to make a clean line between the points.

type Point struct {
	X	int
	Y	int
}

func line(x1, y1, x2, y2 int) []Point {

	if x1 == x2 {
		return lineVertical(x1, y1, y2)
	}
	if y1 == y2 {
		return lineHorizontal(x1, y1, x2)
	}

	dx := x1 - x2
	dy := y1 - y2
	if dx < 0 { dx *= -1 }
	if dy < 0 { dy *= -1 }

	if dy < dx {
		return lineGentle(x1, y1, x2, y2)
	} else {
		return lineSteep(x1, y1, x2, y2)
	}
}

func lineHorizontal(x1, y, x2 int) []Point {

	var points []Point

	if x1 > x2 {
		x1, x2 = x2, x1
	}

	for x := x1 ; x <= x2 ; x++ {
		points = append(points, Point{x, y})
	}

	return points
}

func lineVertical(x, y1, y2 int) []Point {

	var points []Point

	if y1 > y2 {
		y1, y2 = y2, y1
	}

	for y := y1 ; y <= y2 ; y++ {
		points = append(points, Point{x, y})
	}

	return points
}

func lineGentle(x1, y1, x2, y2 int) []Point {

	// Based on an algorithm I read on the web 15 years ago;
	// The webpage has long since vanished.

	var points []Point

	var additive int

	if x1 > x2 {
		x1, x2 = x2, x1
		y1, y2 = y2, y1
	}

	if (y1 < y2) {
		additive = 1;
	} else {
		additive = -1;
	}

	dy_times_two := (y2 - y1) * 2
	if dy_times_two < 0 { dy_times_two *= -1 }

	dx_times_two := (x2 - x1) * 2       // We know we're going right, no need to check for < 0

	the_error := x1 - x2

	for n := x1 ; n <= x2 ; n++ {

		points = append(points, Point{n, y1})

		the_error += dy_times_two;
		if the_error > 0 {
			y1 += additive
			the_error -= dx_times_two
		}
	}

	return points
}

func lineSteep(x1, y1, x2, y2 int) []Point {

	var points []Point

	var additive int

	if y1 > y2 {
		x1, x2 = x2, x1
		y1, y2 = y2, y1
	}

	if (x1 < x2) {
		additive = 1;
	} else {
		additive = -1;
	}

	dy_times_two := (y2 - y1) * 2       // We know we're going down, no need to check for < 0

	dx_times_two := (x2 - x1) * 2
	if dx_times_two < 0 { dx_times_two *= -1 }

	the_error := y1 - y2;

	for n := y1 ; n <= y2 ; n++ {

		points = append(points, Point{x1, n})

		the_error += dx_times_two
		if the_error > 0 {
			x1 += additive
			the_error -= dy_times_two
		}
	}

	return points
}
