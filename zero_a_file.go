package main

import (
	"fmt"
	"os"
)

func main() {
	args := os.Args[1:]
	for _, fpath := range args {
		overwrite(fpath)
	}
}

func overwrite(fpath string) {
	f, err := os.OpenFile(fpath, os.O_RDWR, 0777)
	if err != nil {
		fmt.Printf("%v\n", err)
		return
	}
	info, err := f.Stat()
	if err != nil {
		fmt.Printf("%v\n", err)
		return
	}
	buf := make([]byte, info.Size())
	f.Seek(0, 0)
	_, err = f.Write(buf)
	if err != nil {
		fmt.Printf("%v\n", err)
		return
	}
}
