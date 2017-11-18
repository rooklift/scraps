package game

var WALL_LOOKUP = [16]string{
	/* 0000 */	"╬",
	/* 0001 */	"═",
	/* 0010 */	"║",
	/* 0011 */	"╝",
	/* 0100 */	"═",
	/* 0101 */	"═",
	/* 0110 */	"╚",
	/* 0111 */	"╩",
	/* 1000 */	"║",
	/* 1001 */	"╗",
	/* 1010 */	"║",
	/* 1011 */	"╣",
	/* 1100 */	"╔",
	/* 1101 */	"╦",
	/* 1110 */	"╠",
	/* 1111 */	"╬",
}

func (self *Object) DrawAsWall() {

	bits := 0

	if self.Area.InBounds(self.X - 1, self.Y) {
		if self.Area.SpeciesExistsAt("Wall", self.X - 1, self.Y) {
			bits += 1
		}
	}

	if self.Area.InBounds(self.X, self.Y - 1) {
		if self.Area.SpeciesExistsAt("Wall", self.X, self.Y - 1) {
			bits += 2
		}
	}

	if self.Area.InBounds(self.X + 1, self.Y) {
		if self.Area.SpeciesExistsAt("Wall", self.X + 1, self.Y) {
			bits += 4
		}
	}

	if self.Area.InBounds(self.X, self.Y + 1) {
		if self.Area.SpeciesExistsAt("Wall", self.X, self.Y + 1) {
			bits += 8
		}
	}

	char := WALL_LOOKUP[bits]

	MAIN_WINDOW.Set(self.ScreenX(), self.ScreenY(), char, self.Colour)
}
