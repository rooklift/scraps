package main

// Split a PNG file into its 4 quadrants...

import (
	"fmt"
	"image"
	"image/png"
	"os"
	"strings"
)

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

	half_width := (bounds.Max.X - bounds.Min.X) / 2
	half_height := (bounds.Max.Y - bounds.Min.Y) / 2

	// Declare what method we require the image to have if we're to crop it...

	type Croppable interface {
		SubImage(r image.Rectangle) image.Image
	}

	// Try to treat the image as satisfying that interface...

	img_as_croppable, ok := img.(Croppable)
	if !ok {
		return fmt.Errorf("%v - can't be cropped!\n", fpath)
	}

	// Perform the crops...

	var results []image.Image

	for j := 0; j <= 1; j++ {
		for i := 0; i <= 1; i++ {
			crop_rect := image.Rect(i * half_width, j * half_height, i * half_width + half_width, j * half_height + half_height)
			results = append(results, img_as_croppable.SubImage(crop_rect))
		}
	}

	// Work out filename sans ".png"...

	filename := strings.TrimSuffix(fpath, ".png")

	// Write...

	for n, result := range results {
		outfile, err := os.Create(fmt.Sprintf("%v (%v).png", filename, n))
		if err != nil {
			return err
		}
		defer outfile.Close()

		err = png.Encode(outfile, result)
		if err != nil {
			return err
		}
	}

	return nil
}
