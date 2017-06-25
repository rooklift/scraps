package main

// Simple minded throttler for file downloads via cgi-bin interface.

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"time"
)

const (
	TIME_FORMAT = "Mon Jan 2 15:04:05 UTC 2006"

	// The lines below need adjusting for your use case.

	WAIT_SECONDS = 10
	FILE_FORMAT = "application/zip"
	ZIPFILE = "FIXME"								// The file we are guarding.
	LAST_REQUEST_FILE = "FIXME"						// Where to store our log.
)

var WAIT_TIME time.Duration = WAIT_SECONDS * time.Second

func refuse(next time.Time) {
	fmt.Printf("Content-type: text/plain\n\n")
	fmt.Printf("Downloads are limited to one download every %d seconds.\n", WAIT_SECONDS)
	fmt.Printf("Next possible download is at: %s\n", next.Format(TIME_FORMAT))
	os.Exit(0)
}

func fail(msg string) {
	fmt.Printf("Content-type: text/plain\n\n")
	fmt.Printf("%s\n", msg)
	os.Exit(1)
}

func allow() {
	infile, err := os.Open(ZIPFILE)
	defer infile.Close()
	if err != nil {
		fail("Something went wrong while attempting to read the archive.")
	}
	fmt.Printf("Content-type: %s\n\n", FILE_FORMAT)
	io.Copy(os.Stdout, infile)
}

func check_last() {

	// Aborts program if insufficient time has elapsed since last request.
	// If the log file is not present, creates it and refuses the request.

	lrf, err := os.Open(LAST_REQUEST_FILE)
	defer lrf.Close()

	if err != nil {
		update_last()
		refuse(time.Now().UTC().Add(WAIT_TIME))
	}

	scanner := bufio.NewScanner(lrf)
	scanner.Scan()

	last_time, err := time.Parse(TIME_FORMAT, scanner.Text())
	if err != nil {
		fail("Couldn't parse last request time.")
	}

	if time.Now().UTC().Sub(last_time) > WAIT_TIME {
		return
	}

	refuse(last_time.Add(WAIT_TIME))
}

func update_last() {
	log, err := os.Create(LAST_REQUEST_FILE)
	defer log.Close()
	if err != nil {
		fail("Couldn't update last request log.")
	}
	fmt.Fprintf(log, "%s\n", time.Now().UTC().Format(TIME_FORMAT))
}

func main() {
	check_last()	// Aborts program if needed.
	update_last()
	allow()
}
