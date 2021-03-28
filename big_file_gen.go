package main

import (
	"bufio"
	"math/rand"
	"os"
)

const MB = 2000

func main() {

	f, _ := os.Create("bigfile.bin")
	w := bufio.NewWriter(f)

	var i uint64

	for i = 0; i < 1024 * 1024 * MB; i++ {
		w.WriteByte(byte(rand.Intn(256)))
	}

}

