package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

// -----------------------------------------------------------------

var parser = NewTokenParser()

// -----------------------------------------------------------------

type Direction int

const (
	WAIT Direction = iota
	UP
	RIGHT
	DOWN
	LEFT
)

func (d Direction) vector() (int, int) {
	switch d {
	case WAIT:	return 0, 0
	case UP:	return 0, -1
	case RIGHT:	return 1, 0
	case DOWN:	return 0, 1
	case LEFT:	return -1, 0
	}
	return 0, 0
}

// -----------------------------------------------------------------

type TokenParser struct {
	scanner     *bufio.Scanner
}

func NewTokenParser() *TokenParser {
	ret := new(TokenParser)
	ret.scanner = bufio.NewScanner(os.Stdin)
	ret.scanner.Split(bufio.ScanWords)
	return ret
}

func (self *TokenParser) Int() int {
	ok := self.scanner.Scan()
	if ok == false {
		err := self.scanner.Err()
		if err != nil {
			panic(fmt.Sprintf("%v", err))
		} else {
			panic(fmt.Sprintf("End of input."))
		}
	}
	ret, err := strconv.Atoi(self.scanner.Text())
	if err != nil {
		panic(fmt.Sprintf("TokenReader.Int(): Atoi failed for \"%v\"", self.scanner.Text()))
	}
	return ret
}

func (self *TokenParser) Bytes() []byte {
	ok := self.scanner.Scan()
	if ok == false {
		err := self.scanner.Err()
		if err != nil {
			panic(fmt.Sprintf("%v", err))
		} else {
			panic(fmt.Sprintf("End of input."))
		}
	}
	c := make([]byte, len(self.scanner.Bytes()))
	copy(c, self.scanner.Bytes())
	return c
}

func (self *TokenParser) String() string {
	ok := self.scanner.Scan()
	if ok == false {
		err := self.scanner.Err()
		if err != nil {
			panic(fmt.Sprintf("%v", err))
		} else {
			panic(fmt.Sprintf("End of input."))
		}
	}
	return self.scanner.Text()
}

// -----------------------------------------------------------------

type World struct {
	Width   			int
	Height  			int
	Cells   			[][]byte
	Entities			[]*Entity
	Player				*Entity

	SanityLossLonely	int
	SanityLossGroup		int
	WandererSpawnTime	int
	WandererLifeTime	int
}

func (self *World) Init() {

	self.Width = parser.Int()
	self.Height = parser.Int()

	self.Cells = make([][]byte, self.Width)
	for x := 0 ; x < self.Width ; x++ {
		self.Cells[x] = make([]byte, self.Height)
	}

	for y := 0 ; y < self.Height ; y++ {
		b := parser.Bytes()
		for x := 0 ; x < self.Width ; x++ {
			self.Cells[x][y] = b[x]
		}
	}

	self.SanityLossLonely = parser.Int()
	self.SanityLossGroup = parser.Int()
	self.WandererSpawnTime = parser.Int()
	self.WandererLifeTime = parser.Int()
}

func (self *World) Update() {

	self.Entities = nil

	count := parser.Int()

	for n := 0 ; n < count ; n++ {
		ent := new(Entity)
		ent.World = self
		ent.EntityType = parser.String()
		ent.Id = parser.Int()
		ent.X = parser.Int()
		ent.Y = parser.Int()
		ent.Param0 = parser.Int()
		ent.Param1 = parser.Int()
		ent.Param2 = parser.Int()

		self.Entities = append(self.Entities, ent)
	}

	self.Player = self.Entities[0]	// Guaranteed in specs.
}

func (self *World) Passable(x, y int) bool {

	if self.InBounds(x, y) == false {
		return false
	}

	if self.Cells[x][y] == '#' {
		return false
	}

	return true
}

func (self *World) InBounds(x, y int) bool {
	if x < 0 || x >= self.Width || y < 0 || y >= self.Height {
		return false
	}
	return true
}

func (self *World) LOS(x1, y1, x2, y2 int) bool {

	// All trivial cases...

	if self.InBounds(x1, y1) == false || self.InBounds(x2, y2) == false {
		return false
	}

	if x1 != x2 && y1 != y2 {
		return false
	}

	if x1 == x2 && y1 == y2 {
		return true
	}

	if y1 == y2 {

		// Horizontal...

		step := 1 ; if x1 > x2 { step = -1 }

		for x := x1 ; x != x2 ; x += step {
			if self.Cells[x][y1] == '#' {
				return false
			}
		}

		return true

	} else if x1 == x2 {

		// Vertical...

		step := 1 ; if y1 > y2 { step = -1 }

		for y := y1 ; y != y2 ; y += step {
			if self.Cells[x1][y] == '#' {
				return false
			}
		}

		return true
	}

	panic("This is impossible.")
}

// -----------------------------------------------------------------

type Entity struct {
	World		*World
	EntityType	string
	Id			int
	X			int
	Y			int
	Param0		int
	Param1		int
	Param2		int
}

func (self *Entity) Moves() []Direction {

	x := self.X
	y := self.Y

	var ret []Direction

	if self.World.Passable(x, y - 1) { ret = append(ret, UP)    }
	if self.World.Passable(x + 1, y) { ret = append(ret, RIGHT) }
	if self.World.Passable(x, y + 1) { ret = append(ret, DOWN)  }
	if self.World.Passable(x - 1, y) { ret = append(ret, LEFT)  }

	return ret
}

func (self *Entity) SendDirection(d Direction) {
	if d == WAIT {
		fmt.Printf("WAIT\n")
	} else {
		vec_x, vec_y := d.vector()
		fmt.Printf("MOVE %v %v\n", self.X + vec_x, self.Y + vec_y)
	}
}

func (self *Entity) FriendScore(x, y int) int {

	// We are considering moving to spot [x,y]
	// How good is that for proximity to other explorers?

	closest := 9999

	for _, ent := range self.World.Entities {

		if ent == self {
			continue
		}

		if ent.EntityType != "EXPLORER" {
			continue
		}

		dist := manhattan(ent.X, ent.Y, x, y)

		if dist < closest {
			closest = dist
		}
	}

	return closest * -1		// So greater distances give worse scores.
}

func (self *Entity) WandererScore(x, y int) int {

	// We are considering moving to spot [x,y]
	// How good is that for avoidance of wanderers?

	for _, ent := range self.World.Entities {

		if ent.EntityType != "WANDERER" {
			continue
		}

		dist := manhattan(ent.X, ent.Y, x, y)

		if dist < 2 {
			return -20
		}
	}

	return 0
}

func (self *Entity) SlasherScore(x, y int) int {

	// We are considering moving to spot [x,y]
	// How good is that for avoidance of slashers?

	los := false
	closest := -1

	for _, ent := range self.World.Entities {

		if ent.EntityType != "SLASHER" {
			continue
		}

		if los == false {
			if self.World.LOS(ent.X, ent.Y, x, y) {
				los = true
			}
		}

		dist := manhattan(ent.X, ent.Y, x, y)

		if closest == -1 || dist < closest {
			closest = dist
		}
	}

	if closest == -1 {		// No slashers on map...
		return 0
	}

	score := closest * 2

	if los {
		score -= 10
	}

	return score
}

func (self *Entity) Score(x, y int) int {
	return self.FriendScore(x, y) + self.WandererScore(x, y) + self.SlasherScore(x, y)
}

func (self *Entity) DirectionScore(d Direction) int {
	vec_x, vec_y := d.vector()
	return self.Score(self.X + vec_x, self.Y + vec_y)
}

// -----------------------------------------------------------------

func main() {

	world := new(World)
	world.Init()

	for {
		world.Update()
		AI(world)
	}
}

func abs(n int) int {
	if n < 0 {
		return -n
	}
	return n
}

func manhattan(x1, y1, x2, y2 int) int {
	return abs(x1 - x2) + abs(y1 - y2)
}

func AI(world *World) {

	player := world.Player

	possible_moves := player.Moves()

	best_move := WAIT
	best_score := player.DirectionScore(WAIT)

	for _, d := range possible_moves {

		score := player.DirectionScore(d)

		if score > best_score {
			best_move = d
			best_score = score
		}
	}

	player.SendDirection(best_move)
}

