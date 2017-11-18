package main

// Convert a folder of PNG files to an animated GIF.
// Strange things may happen if the input files vary in size.

import (
	"fmt"
	"image"
	"image/color/palette"
	"image/draw"
	"image/gif"
	"image/png"
	"io/ioutil"
	"os"
	"path/filepath"
)

func work(files []string) {

	out_gif := new(gif.GIF)

	for _, name := range files {

		f, _ := os.Open(name)
		input, err := png.Decode(f)
		f.Close()

		if err != nil {
			continue
		}

		paletted_image := image.NewPaletted(input.Bounds(), palette.Plan9)
		draw.Draw(paletted_image, paletted_image.Rect, input, input.Bounds().Min, draw.Over)

		out_gif.Image = append(out_gif.Image, paletted_image)
		out_gif.Delay = append(out_gif.Delay, 125)
	}

	f, _ := os.Create("out.gif")
	gif.EncodeAll(f, out_gif)
	f.Close()
}

func main() {

	if len(os.Args) == 1 {
		fmt.Printf("Need argument: directory\n")
		return
	}

	fileinfos, err := ioutil.ReadDir(os.Args[1])
	if err != nil {
		fmt.Printf("%v\n", err)
		return
	}

	var filenames []string

	for _, f := range fileinfos {
		if f.IsDir() == false {
			filenames = append(filenames, filepath.Join(os.Args[1], f.Name()))
		}
	}

	work(filenames)
}
