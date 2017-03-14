// Monte Carlo estimation of Pi

package main

import (
    "fmt"
    "math"
    "math/rand"
)

const TRIALS = 10000000

func main () {

    in := 0

    for n := 0 ; n < TRIALS ; n++ {

        x := rand.Float64()
        y := rand.Float64()

        dx := x - 0.5
        dy := y - 0.5

        if math.Sqrt(dx * dx + dy * dy) < 0.5 {
            in++
        }
    }

    area := float64(in) / TRIALS
    pi := area / 0.25

    fmt.Printf("%.6f\n", pi)
}
