package main

// Turing machine capable of reproducing Wikipedia's Busy Beaver 5 contender.

import (
	"fmt"
	"strings"
)

// Format: input bit, current state --> output bit, movement, new state or HALT.
// Note that the first named state (here "A") will be the initial state.
const RULES_STRING = `
0,A,1,R,B
1,A,1,L,C
0,B,1,R,C
1,B,1,R,B
0,C,1,R,D
1,C,0,L,E
0,D,1,L,A
1,D,1,L,D
0,E,1,R,HALT
1,E,0,L,A
`

type Rule [2]Action							// Each state's rule has 2 possible actions, chosen depending on the input bit.

type Action struct {
	NewBit		bool						// The bit to write to the current position.
	Move		int							// -1, 0, 1
	NewState	int							// The state to switch to after moving, or -1 to halt.
}

type Machine struct {
	Rules		[]Rule
	Tape		[]byte						// Each byte encodes eight bits.
	State		int
	Pos			int
	Subpos		int							// The bit of the byte we are at, numbered from the left.
	Steps		int
}

func NewMachine(rules []Rule) *Machine {
	ret := new(Machine)
	ret.Rules = rules
	ret.Tape = make([]byte, 1, 1)
	ret.State = 0							// Will be -1 if halted.
	ret.Pos = 0
	ret.Subpos = 0
	ret.Steps = 0
	return ret
}

func (self *Machine) Extend(left bool) {	// Extend the tape when needed (to the left or right, as per the arg).
	old_len := len(self.Tape)
	new_len := old_len * 2
	new_tape := make([]byte, new_len, new_len)
	if (left) {
		copy(new_tape[old_len:], self.Tape)
		self.Pos = self.Pos + old_len
	} else {
		copy(new_tape, self.Tape)
	}
	self.Tape = new_tape
}

func (self *Machine) ExtendLeft() {
	self.Extend(true)
}

func (self *Machine) ExtendRight() {
	self.Extend(false)
}

func (self *Machine) GetBit() bool {		// The bit at the current position, expressed as a bool.
	b := self.Tape[self.Pos]
	switch self.Subpos {
		case 0: return b & 0b10000000 > 0
		case 1: return b & 0b01000000 > 0
		case 2: return b & 0b00100000 > 0
		case 3: return b & 0b00010000 > 0
		case 4: return b & 0b00001000 > 0
		case 5: return b & 0b00000100 > 0
		case 6: return b & 0b00000010 > 0
		case 7: return b & 0b00000001 > 0
		default: panic("Bad Subpos")
	}
}

func (self *Machine) SetBit(val bool) {
	if val {
		switch self.Subpos {
			case 0: self.Tape[self.Pos] |= 0b10000000
			case 1: self.Tape[self.Pos] |= 0b01000000
			case 2: self.Tape[self.Pos] |= 0b00100000
			case 3: self.Tape[self.Pos] |= 0b00010000
			case 4: self.Tape[self.Pos] |= 0b00001000
			case 5: self.Tape[self.Pos] |= 0b00000100
			case 6: self.Tape[self.Pos] |= 0b00000010
			case 7: self.Tape[self.Pos] |= 0b00000001
			default: panic("Bad Subpos")
		}
	} else {
		switch self.Subpos {
			case 0: self.Tape[self.Pos] &= 0b01111111
			case 1: self.Tape[self.Pos] &= 0b10111111
			case 2: self.Tape[self.Pos] &= 0b11011111
			case 3: self.Tape[self.Pos] &= 0b11101111
			case 4: self.Tape[self.Pos] &= 0b11110111
			case 5: self.Tape[self.Pos] &= 0b11111011
			case 6: self.Tape[self.Pos] &= 0b11111101
			case 7: self.Tape[self.Pos] &= 0b11111110
			default: panic("Bad Subpos")
		}
	}
}

func (self *Machine) MoveLeft() {
	self.Subpos -= 1
	if self.Subpos < 0 {
		self.Subpos = 7
		self.Pos -= 1
		if self.Pos < 0 {
			self.ExtendLeft()
		}
	}
}

func (self *Machine) MoveRight() {
	self.Subpos += 1
	if self.Subpos > 7 {
		self.Subpos = 0
		self.Pos += 1
		if self.Pos >= len(self.Tape) {
			self.ExtendRight()
		}
	}
}

func (self *Machine) Popcount() int {		// How many 1s on the tape.
	count := 0
	for _, b := range self.Tape {
		for i := 0; i < 8; i++ {
			if b >> i & 1 == 1 {
				count++
			}
		}
	}
	return count
}

func (self *Machine) Step() {

	if self.State < 0 {
		panic("Already halted")
	}

	bit := 0
	if self.GetBit() {
		bit = 1
	}

	action := self.Rules[self.State][bit]

	self.SetBit(action.NewBit)

	switch action.Move {
		case -1: self.MoveLeft()
		case  0: // Pass (Golang doesn't fallthrough by default)
		case  1: self.MoveRight()
		default: panic("Bad Move")
	}

	self.State = action.NewState

	self.Steps++
}

// ------------------------------------------------------------------------------------------------

func ParseRules(s string) []Rule {

	// Turn a rules string (see top) into an array of rules.
	// We'll assign each named state its own integer. These will become the indices in the final array.

	state_num_map := make(map[string]int)

	halt_exists := false

	for _, line := range strings.Split(s, "\n") {
		if strings.Count(line, ",") != 4 {
			continue
		}
		parts := strings.Split(line, ",")
		if parts[1] == "HALT" {
			panic("Defining actions for the HALT state is not allowed.")
		}
		if parts[4] == "HALT" {
			halt_exists = true
		}
		for _, state := range []string{parts[1], parts[4]} {
			_, ok := state_num_map[state]
			if !ok && state != "HALT" {
				state_num_map[state] = len(state_num_map)
			}
		}
	}

	if !halt_exists {
		panic("Rules didn't include HALT")
	}

	// Now we know how many states there are...

	ret := make([]Rule, len(state_num_map))

	// Lets say that, by default, everything halts...

	for _, rule := range ret {
		rule[0].NewState = -1
		rule[1].NewState = -1
	}

	// Now we can parse properly...

	for _, line := range strings.Split(s, "\n") {

		if strings.Count(line, ",") != 4 {
			continue
		}

		parts := strings.Split(line, ",")

		old_state_num, ok1 := state_num_map[parts[1]]
		new_state_num, ok2 := state_num_map[parts[4]]

		if !ok1 {
			panic("Wat")
		}

		if !ok2 {
			if parts[4] == "HALT" {			// The only valid reason why this state isn't in the state_num_map.
				new_state_num = -1
			} else {
				panic("Wat")
			}
		}

		var input_bit int					// Int because we use it as an index to access an array.
		switch parts[0] {
			case "0": input_bit = 0
			case "1": input_bit = 1
			default: panic("Bad rule")
		}

		var output_bit bool
		switch parts[2] {
			case "0": output_bit = false
			case "1": output_bit = true
			default: panic("Bad rule")
		}

		var move int
		switch parts[3] {
			case "L": move = -1
			case "N": move = 0
			case "R": move = 1
			default: panic("Bad rule")
		}

		ret[old_state_num][input_bit].NewBit = output_bit
		ret[old_state_num][input_bit].Move = move
		ret[old_state_num][input_bit].NewState = new_state_num
	}

	return ret

}


func main() {

	rules := ParseRules(RULES_STRING)
	machine := NewMachine(rules)

	for machine.State != -1 {
		machine.Step()
	}

	fmt.Printf("Halted!\n\t   Steps: %v\n\tPopcount: %v\n", machine.Steps, machine.Popcount())

}
