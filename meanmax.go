package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"sort"
	"strconv"
)

const (
	REAPER int = iota
	DESTROYER
	DOOF
	TANKER
	WRECK
	TAR
	OIL
)

type Unit struct {
	Id					int
	Type				int
	Owner				int
	Mass				float64
	Radius				int
	X					int
	Y					int
	Speedx				int
	Speedy				int
	Extra				int
	Extra2				int
}

func (self *Unit) Dist(other *Unit) float64 {
	dx := float64(other.X - self.X)
	dy := float64(other.Y - self.Y)
	return math.Sqrt(dx * dx + dy * dy)
}

func (self *Unit) Angle(other *Unit) float64 {
	rad := math.Atan2(float64(other.Y - self.Y), float64(other.X - self.X))
	deg := RadToDeg(rad)
	for deg < 0 { deg += 360 }
	for deg >= 360 { deg -= 360 }
	return deg
}

type State struct {

	Scores				[3]int
	Rages				[3]int

	// These will be kept in order, e.g. Reapers[0] is mine.

	Reapers				[3]*Unit
	Destroyers			[3]*Unit
	Doofs				[3]*Unit

	// No assumptions should be made that the following are in any particular order.

	Tankers				[]*Unit
	Wrecks				[]*Unit
	Tarpools			[]*Unit
	Oilpools			[]*Unit
}

type Moves struct {
	Reaper				string
	Destroyer			string
	Doof				string
}

var parser = NewTokenParser()

func get_state() *State {

	ret := new(State)

	for n := 0; n < 3; n++ {
		ret.Scores[n] = parser.Int()
	}

	for n := 0; n < 3; n++ {
		ret.Rages[n] = parser.Int()
	}

	unit_count := parser.Int()

	for n := 0; n < unit_count; n++ {

		u := new(Unit)

		u.Id,         u.Type,       u.Owner,      u.Mass,         u.Radius,     u.X,          u.Y,          u.Speedx,     u.Speedy,     u.Extra,      u.Extra2 =
		parser.Int(), parser.Int(), parser.Int(), parser.Float(), parser.Int(), parser.Int(), parser.Int(), parser.Int(), parser.Int(), parser.Int(), parser.Int()

		switch u.Type {
			case REAPER:	ret.Reapers[u.Owner] = u
			case DESTROYER:	ret.Destroyers[u.Owner] = u
			case DOOF:		ret.Doofs[u.Owner] = u
			case TANKER:	ret.Tankers = append(ret.Tankers, u)
			case WRECK:		ret.Wrecks = append(ret.Wrecks, u)
			case TAR:		ret.Tarpools = append(ret.Tarpools, u)
			case OIL:		ret.Oilpools = append(ret.Oilpools, u)
			default:		fmt.Fprintf(os.Stderr, "Got unknown unit type %d", u.Type)
		}
	}

	return ret
}

// ----------------------------------------------------

func main() {
	for {
		state := get_state()
		moves := choose_moves(state)
		fmt.Printf("%s\n%s\n%s\n", moves.Reaper, moves.Destroyer, moves.Doof)
	}
}

func choose_moves(s *State) Moves {

	moves := Moves{"WAIT", "WAIT", "WAIT"}

	reaper := s.Reapers[0]

	// Reaper...

	if len(s.Wrecks) > 0 {

		sort.Slice(s.Wrecks, func(a, b int) bool {
			return s.Wrecks[a].Dist(reaper) < s.Wrecks[b].Dist(reaper)
		})

		/*

		sort.Slice(s.Wrecks, func(a, b int) bool {		// Score by my advantage over the closest enemy reaper in getting there...

			wreck_a := s.Wrecks[a]
			wreck_b := s.Wrecks[b]

			var wreck_a_close_enemy, wreck_b_close_enemy *Unit

			if wreck_a.Dist(s.Reapers[1]) < wreck_a.Dist(s.Reapers[2]) {
				wreck_a_close_enemy = s.Reapers[1]
			} else {
				wreck_a_close_enemy = s.Reapers[2]
			}

			if wreck_b.Dist(s.Reapers[1]) < wreck_b.Dist(s.Reapers[2]) {
				wreck_b_close_enemy = s.Reapers[1]
			} else {
				wreck_b_close_enemy = s.Reapers[2]
			}

			return reaper.Dist(wreck_a) - wreck_a_close_enemy.Dist(wreck_a) < reaper.Dist(wreck_b) - wreck_b_close_enemy.Dist(wreck_b)
		})

		*/

		moves.Reaper = fmt.Sprintf("%d %d %d", s.Wrecks[0].X, s.Wrecks[0].Y, 300)
	}

	// Destroyer...

	if len(s.Tankers) > 0 {

		sort.Slice(s.Tankers, func(a, b int) bool {
			return s.Tankers[a].Dist(reaper) < s.Tankers[b].Dist(reaper)
		})

		moves.Destroyer = fmt.Sprintf("%d %d %d", s.Tankers[0].X, s.Tankers[0].Y, 300)
	}

	// Doof...

	hsid := 1		// High scoring enemy ID

	if s.Scores[2] > s.Scores[1] {
		hsid = 2
	}

	moves.Doof = fmt.Sprintf("%d %d %d", s.Reapers[hsid].X, s.Reapers[hsid].Y, 300)

	return moves
}

// ----------------------------------------------------

type TokenParser struct {
	scanner		*bufio.Scanner
	count		int
}

func NewTokenParser() *TokenParser {
	ret := new(TokenParser)
	ret.scanner = bufio.NewScanner(os.Stdin)
	ret.scanner.Split(bufio.ScanWords)
	return ret
}

func (self *TokenParser) Int() int {
	bl := self.scanner.Scan()
	if bl == false {
		err := self.scanner.Err()
		if err != nil {
			panic(fmt.Sprintf("%v", err))
		} else {
			panic(fmt.Sprintf("End of input."))
		}
	}
	ret, err := strconv.Atoi(self.scanner.Text())
	if err != nil {
		panic(fmt.Sprintf("TokenReader.Int(): Atoi failed at token %d: \"%s\"", self.count, self.scanner.Text()))
	}
	self.count++
	return ret
}

func (self *TokenParser) Float() float64 {
	bl := self.scanner.Scan()
	if bl == false {
		err := self.scanner.Err()
		if err != nil {
			panic(fmt.Sprintf("%v", err))
		} else {
			panic(fmt.Sprintf("End of input."))
		}
	}
	ret, err := strconv.ParseFloat(self.scanner.Text(), 64)
	if err != nil {
		panic(fmt.Sprintf("TokenReader.Float(): ParseFloat failed at token %d: \"%s\"", self.count, self.scanner.Text()))
	}
	self.count++
	return ret
}

// ----------------------------------------------------

func RadToDeg(r float64) float64 {
	return r / math.Pi * 180
}
