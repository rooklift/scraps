package main

import (
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
)

// Input via command line e.g. 52...6.........7.13...........4..8..6......5...........418.........3..2...87.....

const VALID_INPUT = "1234567890."

type Point struct {
	x	int
	y	int
}

type Board struct {
	vals 			[9][9]int
	solve_order		[]Point
	steps			int
}

func (self *Board) Load(s string) {

	var x, y int
	var err error

	for _, c := range s {

		if strings.Contains(VALID_INPUT, string(c)) == false {
			continue
		}

		self.vals[x][y], _ = strconv.Atoi(string(c))		// Returns 0 on failure, which is fine since that's our "unknown" flag.

		x, y, err = next_xy(x, y)

		if err != nil {										// We reached the end.
			break
		}
	}

	self.ChooseSolveOrder()
}

func (self *Board) Print() {
	fmt.Printf("\n")
	for y := 0; y < 9; y++ {
		fmt.Printf("\t")
		for x := 0; x < 9; x++ {
			if self.vals[x][y] != 0 {
				fmt.Printf("%d", self.vals[x][y])
			} else {
				fmt.Printf(".")
			}
			if x == 2 || x == 5 {
				fmt.Printf("|")
			}
		}
		fmt.Printf("\n")
		if y == 2 || y == 5 {
			fmt.Printf("\t---|---|---\n")
		}
	}
	fmt.Printf("\n\t%d steps.\n\n", self.steps)
}

func (self *Board) CalculatePossibles(x, y int) []int {

	if self.vals[x][y] != 0 {
		return []int{self.vals[x][y]}
	}

	var eliminated [10]bool		// zeroth index is unused
	var ret []int

	// Eliminate via horizontal rule...

	for i := 0; i < 9; i++ {
		val := self.vals[i][y]
		if val != 0 {
			eliminated[val] = true
		}
	}

	// Eliminate via vertical rule...

	for j := 0; j < 9; j++ {
		val := self.vals[x][j]
		if val != 0 {
			eliminated[val] = true
		}
	}

	// Eliminate via 3x3 box rule...
	// Note: a lot of overlap with the above.

	a := (x / 3) * 3
	b := (y / 3) * 3

	for i := a; i < a + 3; i++ {
		for j := b; j < b + 3; j++ {
			val := self.vals[i][j]
			if val != 0 {
				eliminated[val] = true
			}
		}
	}

	for n := 1; n <= 9; n++ {
		if eliminated[n] == false {
			ret = append(ret, n)
		}
	}

	return ret
}

func next_xy(x, y int) (int, int, error) {
	x += 1
	if x >= 9 {
		x = 0
		y += 1
		if y >= 9 {
			return 0, 0, fmt.Errorf("End of sequence")
		}
	}
	return x, y, nil
}

func (self *Board) ChooseSolveOrder() {

	for x := 0; x < 9; x++ {
		for y := 0; y < 9; y++ {
			if self.vals[x][y] == 0 {
				self.solve_order = append(self.solve_order, Point{x, y})
			}
		}
	}

	sort.SliceStable(self.solve_order, func(a, b int) bool {
		a_poss := len(self.CalculatePossibles(self.solve_order[a].x, self.solve_order[a].y))
		b_poss := len(self.CalculatePossibles(self.solve_order[b].x, self.solve_order[b].y))
		return a_poss < b_poss
	})
}

func (self *Board) Solve(depth int) bool {

	self.steps++

	if depth >= len(self.solve_order) {
		return true
	}

	x, y := self.solve_order[depth].x, self.solve_order[depth].y

	// Solve for the board starting at x,y.
	// Recurses by calling itself with the next values of x,y.
	// Returns false if the board was not solvable.
	// Must not change the board if returning false.

	if self.vals[x][y] != 0 {

		// We already have the value for this square, so recurse right away...
		// return self.Solve(depth + 1)

		panic("Already had value.")		// This should be impossible.
	}

	possibles := self.CalculatePossibles(x, y)

	if len(possibles) == 0 {
		return false
	}

	for _, p := range possibles {

		// Try recursing for each possible value here.

		self.vals[x][y] = p

		ok := self.Solve(depth + 1)

		if ok {
			return true
		}
	}

	// The board was not solvable. We must not change the board,
	// so clear this point.

	self.vals[x][y] = 0
	return false
}

func main() {
	if len(os.Args) == 1 {
		fmt.Printf("Supply a puzzle via command line.\n")
		fmt.Printf("e.g. 52...6.........7.13...........4..8..6......5...........418.........3..2...87.....\n")
		return
	}
	b := Board{}
	input := strings.Join(os.Args[1:], "")
	b.Load(input)
	b.Solve(0)
	b.Print()
}

