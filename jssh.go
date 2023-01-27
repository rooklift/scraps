package kit

// UPDATE: THIS WAS PROBABLY POINTLESS SINCE DECODERS LIKELY DON'T HAVE THE ISSUE I WAS IMAGINING THEM TO HAVE.
//
// The problem: we are sent JSON lines, but they can be very long. I can't immediately see a clean way of handling
// that in the Golang standard library. We want to stream the data in with a json.Decoder but I note that a Decoder
// "may read data from r beyond the JSON values requested" which sounds troublesome. Therefore I will indeed use a
// Decoder, but point it at a special reader which won't go past \n until unpaused manually.
//
// There's probably some really simple alternative that I've missed.

import (
	"bufio"
	"os"
)

type JSSH struct {						// JSON Stdin Stream Helper
	buffer			[]byte
	bufio_reader	*bufio.Reader
	paused			bool				// true if we hit a newline in source
}

// The plan:
// Return data until a newline is encountered, then:
// Return newlines (not from any source) until unpaused

func new_jssh() *JSSH {
	ret := new(JSSH)
	ret.bufio_reader = bufio.NewReader(os.Stdin)
	return ret
}

func (self *JSSH) Unpause() {
	self.paused = false
}

func (self *JSSH) Read(p []byte) (int, error) {
	if (len(p) == 0) {
		return 0, nil
	} else if self.paused {
		return self.read_while_paused(p)
	} else {
		return self.read_while_unpaused(p)
	}
}

func (self *JSSH) read_while_paused(p []byte) (int, error) {
	if len(self.buffer) > 0 {
		return self.perform_transfer(p)
	} else {
		p[0] = '\n'
		return 1, nil
	}
}

func (self *JSSH) read_while_unpaused(p []byte) (int, error) {
	if len(self.buffer) > 0 {
		return self.perform_transfer(p)
	} else {
		line, is_prefix, err := self.bufio_reader.ReadLine()
		if err != nil {
			return 0, err
		}
		if is_prefix == false {
			self.paused = true
		}
		self.buffer = line
		return self.perform_transfer(p)
	}
}

func (self *JSSH) perform_transfer(p []byte) (int, error) {
	count := copy(p, self.buffer)
	if count == len(self.buffer) {
		self.buffer = nil
	} else {
		self.buffer = self.buffer[count:]
	}
	return count, nil
}
