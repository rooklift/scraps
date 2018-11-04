package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"sort"

	"./sim"
)

type Result struct {
	Seed		uint32
	Size		int
	Players		int
	Score		int
}

type SaveFile struct {
	N			uint32
	Seeds		[]uint32
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

	n := uint32(0)
	results := make(map[string]Result)

	defer finish(&n, results)

	// -------------------------------------------------

	var load SaveFile

	injson, err := ioutil.ReadFile("known_seeds.json")

	if err != nil {
		fmt.Printf("%v\n", err)
	} else {
		err = json.Unmarshal(injson, &load)
		if err != nil {
			fmt.Printf("%v\n", err)
		}
	}

	// -------------------------------------------------

	for _, n = range load.Seeds {

		size := sim.SizeFromSeed(n)

		for players := 2; players <= 4; players += 2 {

			high_key := fmt.Sprintf("%v-%v-%v", "high", players, size)
			low_key := fmt.Sprintf("%v-%v-%v", "low", players, size)

			frame := sim.MapGenOfficial(players, size, size, 5000, n)
			result := Result{n, size, players, frame.TotalHalite()}

			if result.Score > results[high_key].Score {
				results[high_key] = result
			}

			if result.Score < results[low_key].Score || results[low_key].Seed == 0 {
				results[low_key] = result
			}
		}
	}

	// -------------------------------------------------

	fmt.Printf("Starting at %v\n", load.N)

	for n = load.N; n < 0xffffffff; n++ {

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
			result := Result{n, size, players, frame.TotalHalite()}

			if result.Score > results[high_key].Score {
				results[high_key] = result
				fmt.Printf("%v: -s %v (halite: %v, avg: %v)\n", high_key, result.Seed, result.Score, result.Score / (result.Size * result.Size))
			}

			if result.Score < results[low_key].Score || results[low_key].Seed == 0 {
				results[low_key] = result
				fmt.Printf("%v: -s %v (halite: %v, avg: %v)\n", low_key, result.Seed, result.Score, result.Score / (result.Size * result.Size))
			}
		}
	}
}

func finish(n *uint32, results map[string]Result) {
	var all_keys []string
	var good_seeds []uint32
	var save SaveFile

	for key, _ := range results {
		all_keys = append(all_keys, key)
	}

	sort.Strings(all_keys)

	fmt.Printf("Ending at %d\n", *n)
	fmt.Printf("--------------------------------------------------------------\n")

	for _, key := range all_keys {
		fmt.Printf("%v: -s %v (halite: %v, avg: %v)\n", key, results[key].Seed, results[key].Score, results[key].Score / (results[key].Size * results[key].Size))
		good_seeds = append(good_seeds, results[key].Seed)
	}

	save.N = *n
	save.Seeds = good_seeds

	outjson, _ := json.Marshal(save)

	outfile, _ := os.Create("known_seeds.json")
	outfile.Write(outjson)
	outfile.Close()

	end_chan <- true
}
