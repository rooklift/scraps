package main

// Split a PNG file into its 4 quadrants...

import (
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"strings"
)

// image.Image is an interface. The underlying object may or may not have the SubImage() method.
// Later we test for this by trying to type switch an image to the following...

type SubImager interface {
	SubImage(r image.Rectangle) image.Image
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

	half_width := (bounds.Max.X - bounds.Min.X) / 2
	half_height := (bounds.Max.Y - bounds.Min.Y) / 2

	// Check if the image has SubImage() method... if yes, treat it as such...

	img_as_croppable, ok := img.(SubImager)
	if !ok {
		return fmt.Errorf("%v - can't be cropped!\n", fpath)
	}

	// Perform the crops... if the app is named top_left or similar, perform only that crop...

	img_path_no_ext := strings.TrimSuffix(fpath, ".png")

	app_basename := filepath.Base(os.Args[0])

	if strings.Contains(app_basename, "top_left") {
		return write_png(img_as_croppable.SubImage(image.Rect(0, 0, half_width, half_height)), img_path_no_ext + " (0).png")
	} else if strings.Contains(app_basename, "top_right") {
		return write_png(img_as_croppable.SubImage(image.Rect(half_width, 0, half_width * 2, half_height)), img_path_no_ext + " (1).png")
	} else if strings.Contains(app_basename, "bottom_left") {
		return write_png(img_as_croppable.SubImage(image.Rect(0, half_height, half_width, half_height * 2)), img_path_no_ext + " (2).png")
	} else if strings.Contains(app_basename, "bottom_right") {
		return write_png(img_as_croppable.SubImage(image.Rect(half_width, half_height, half_width * 2, half_height * 2)), img_path_no_ext + " (3).png")
	} else {
		for n := 0; n <= 3; n++ {
			i := n % 2
			j := n / 2
			crop_rect := image.Rect(i * half_width, j * half_height, i * half_width + half_width, j * half_height + half_height)
			err := write_png(img_as_croppable.SubImage(crop_rect), fmt.Sprintf("%v (%v).png", img_path_no_ext, n))
			if err != nil {
				return err
			}
		}
	}

	return nil
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
