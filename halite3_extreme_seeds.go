package main

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"./sim"
)

type Result struct {
	Seed		uint32
	Score		int
}

var end_chan = make(chan bool)

func main() {
	go runner()
	input := bufio.NewScanner(os.Stdin)
	input.Scan()
	end_chan <- true
	<- end_chan
}

func runner() {

	results := make(map[string]Result)

	defer func() {

		var all_keys []string

		for key, _ := range results {
			all_keys = append(all_keys, key)
		}

		sort.Strings(all_keys)

		for _, key := range all_keys {
			fmt.Printf("%v: -s %v (halite: %v)\n", key, results[key].Seed, results[key].Score)
		}

		end_chan <- true
	}()

	// -------------------------------------------------

	for n := uint32(0); n < 0xffffffff; n++ {

		if n % 100 == 0 {
			select {
			case <- end_chan:
				return
			default:
				// pass
			}
		}

		size := sim.SizeFromSeed(n)

		for players := 2; players <= 4; players += 2 {

			high_key := fmt.Sprintf("%v-%v-%v", "high", players, size)
			low_key := fmt.Sprintf("%v-%v-%v", "low", players, size)

			frame := sim.MapGenOfficial(players, size, size, 5000, n)
			th := frame.TotalHalite()

			if th > results[high_key].Score {
				results[high_key] = Result{n, th}
			}

			if th < results[low_key].Score || results[low_key].Seed == 0 {
				results[low_key] = Result{n, th}
			}
		}
	}
}
