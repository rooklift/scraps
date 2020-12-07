package main

// Display raw responses to HTTP requests
// (stops after a certain number of bytes)

import (
	"bufio"
	"fmt"
	"net/http"
	"net/http/httputil"
	"os"
	"strings"
)

const BYTES_TO_SHOW = 2048

func getline()  string {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
	return scanner.Text()
}

func main()  {
	for {
		fmt.Printf("> ")
		url := getline()

		if strings.Index(url, "http://") == -1 {
			if strings.Index(url, "https://") == -1 {
				url = "http://" + url
			}
		}

		resp, err := http.Get(url)
	    if err != nil {
	        fmt.Printf("error calling http.Get: %s\n", err)
			continue
	    }

		dump, _ := httputil.DumpResponse(resp, true)

		upperbound := BYTES_TO_SHOW
		if upperbound > len(dump) {
			upperbound = len(dump)
		}

		fmt.Println()
		os.Stdout.Write(dump[0:upperbound])
		fmt.Println()
		fmt.Println()

		resp.Body.Close()
	}
}
