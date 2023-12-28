package main

// Flip a PNG image horizontally...

import (
	"image/color"
	"fmt"
	"image"
	"image/png"
	"os"
	"strings"
)

// image.Image is an interface. The underlying object may or may not have the Set() method.
// Later we test for this by trying to type switch an image to the following...

type Setter interface {
	At(x, y int) color.Color
	Bounds() image.Rectangle
	ColorModel() color.Model
	Set(x, y int, c color.Color)
}

func main() {
	args := os.Args[1:]
	for _, fpath := range args {
		err := handle(fpath)
		if err != nil {
			fmt.Printf("%v\n", err)
		}
	}
}

func handle(fpath string) error {

	// Load the PNG...

	f, err := os.Open(fpath)
	if err != nil {
		return err
	}

	img, err := png.Decode(f)
	if err != nil {
		return err
	}

	// Calculate sizes...

	bounds := img.Bounds()

	if bounds.Min.X != 0 || bounds.Min.Y != 0 {
		return fmt.Errorf("%v - Min was not (0,0) point!\n", fpath)
	}

	width := bounds.Max.X - bounds.Min.X
	height := bounds.Max.Y - bounds.Min.Y

	// Check if the image has Set() method... if yes, treat it as such...

	img_as_settable, ok := img.(Setter)
	if !ok {
		return fmt.Errorf("%v - can't have pixels set!\n", fpath)
	}

	img_path_no_ext := strings.TrimSuffix(fpath, ".png")

	for y := 0; y < height; y++ {
		for x := 0; x < width / 2; x++ {
			left := img_as_settable.At(x, y)
			right := img_as_settable.At(width - 1 - x, y)
			img_as_settable.Set(x, y, right)
			img_as_settable.Set(width - 1 - x, y, left)
		}
	}

	return write_png(img_as_settable, img_path_no_ext + " (flip).png")
}

func write_png(img image.Image, fpath string) error {
	outfile, err := os.Create(fpath)
	if err != nil {
		return err
	}
	defer outfile.Close()
	err = png.Encode(outfile, img)
	if err != nil {
		return err
	}
	return nil
}
