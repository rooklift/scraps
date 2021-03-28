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

	for i = 0; i < (1024 * 1024 * MB) / 8; i++ {

		eight := rand.Uint64()

		for shift := 0; shift <= 56; shift += 8 {
			w.WriteByte(byte(eight << shift))
		}
	}
}

