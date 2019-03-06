package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

// ---------------------------------------

type TokenParser struct {
	scanner			*bufio.Scanner
	count			int
}

func NewTokenParser() *TokenParser {
	ret := new(TokenParser)
	ret.scanner = bufio.NewScanner(os.Stdin)
	ret.scanner.Split(bufio.ScanWords)
	return ret
}

func (self *TokenParser) Int() int {
	ret, err := strconv.Atoi(self.Str())
	if err != nil {
		panic(fmt.Sprintf("TokenParser.Int(): Atoi failed at token %d: \"%s\"", self.count, self.scanner.Text()))
	}
	return ret
}

func (self *TokenParser) Float() float64 {
	ret, err := strconv.ParseFloat(self.Str(), 64)
	if err != nil {
		panic(fmt.Sprintf("TokenParser.Float(): ParseFloat failed at token %d: \"%s\"", self.count, self.scanner.Text()))
	}
	return ret
}

func (self *TokenParser) Str() string {
	bl := self.scanner.Scan()
	if bl == false {
		err := self.scanner.Err()
		if err != nil {
			panic(fmt.Sprintf("TokenParser: %v", err))
		} else {
			panic(fmt.Sprintf("TokenParser: End of input after %d tokens.", self.count))
		}
	}
	self.count++
	return self.scanner.Text()
}

// ---------------------------------------

var token_parser = NewTokenParser()

// ---------------------------------------

func main() {
	return
}
