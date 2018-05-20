package main

/* Indexing Convention:

	x - layer
	y - neuron inside layer
	z - for weights, what the neuron index is from the previous layer

	Note that the weights are indexed according to their right side neuron,
	so there are no weights with x == 0.

*/

import (
	"fmt"
	"math"
)

func sigmoid(x float64) float64 {		// Takes any number and returns a result between 0 and 1.
	return 1 / (1 + math.Exp(-x))
}

type FeedForward struct {
	Values [][]float64
	Biases [][]float64
	Weights [][][]float64
}

func (self *FeedForward) Init(layer_sizes ...int) {

	self.Values = make([][]float64, len(layer_sizes))
	self.Biases = make([][]float64, len(layer_sizes))
	self.Weights = make([][][]float64, len(layer_sizes))

	for x := 0; x < len(layer_sizes); x++ {

		self.Values[x] = make([]float64, layer_sizes[x])
		self.Biases[x] = make([]float64, layer_sizes[x])
		self.Weights[x] = make([][]float64, layer_sizes[x])

		if x > 0 {
			for y := 0; y < layer_sizes[x]; y++ {
				self.Weights[x][y] = make([]float64, layer_sizes[x - 1])
			}
		}
	}
}

func (self *FeedForward) SetWeight(x, y, z int, val float64) {		// z being the index (y index) of the input neuron
	self.Weights[x][y][z] = val
}

func (self *FeedForward) SetValue(x, y int, val float64) {
	self.Values[x][y] = val
}

func (self *FeedForward) GetValue(x, y int) float64 {
	return self.Values[x][y]
}

func (self *FeedForward) Compute() {

	for x := 1; x < len(self.Values); x++ {			// Can't compute layer 0, so start at 1.

		for y := 0; y < len(self.Values[x]); y++ {

			sum := 0.0

			for z := 0; z < len(self.Values[x - 1]); z++ {
				sum += self.Values[x - 1][z] * self.Weights[x][y][z]
			}

			self.Values[x][y] = sigmoid(sum + self.Biases[x][y])

		}
	}
}


func main() {
	net := new(FeedForward)
	net.Init(8,256)

	net.SetValue(0, 0, 1.0)
	net.SetWeight(1, 0, 0, 5.5)
	net.SetWeight(1, 1, 0, 1.0)
	net.Compute()

	fmt.Println(net.GetValue(1, 0))
	fmt.Println(net.GetValue(1, 1))
	fmt.Println(net.GetValue(1, 2))
}
