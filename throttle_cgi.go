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
	FILENAME = "throttle_cgi.go"					// The file we are guarding.
	LAST_REQUEST_FILE = "FIXME"						// Where to store our log.
)

var WAIT_TIME time.Duration = WAIT_SECONDS * time.Second

func refuse(next time.Time) {
	fmt.Printf("Content-type: text/plain\n\n")
	fmt.Printf("Downloads are limited to one download every %d seconds.\n", WAIT_SECONDS)
	fmt.Printf("Next possible download is at: %s\n", next.Format(TIME_FORMAT))
}

func fail(msg string) {
	fmt.Printf("Content-type: text/plain\n\n")
	fmt.Printf("%s\n", msg)
}

func succeed() {
	infile, err := os.Open(FILENAME)
	defer infile.Close()
	if err != nil {
		fail("Something went wrong while attempting to read the archive.")
		return
	}
	fmt.Printf("Content-type: %s\n\n", FILE_FORMAT)
	io.Copy(os.Stdout, infile)
}

func last_success() (time.Time, error) {

	log, err := os.Open(LAST_REQUEST_FILE)
	defer log.Close()

	if err != nil {
		err = update_last()
		if err != nil {
			return time.Time{}, fmt.Errorf("last_success(): error in update_last(): %v", err)
		}
		return time.Now().UTC(), nil
	}

	scanner := bufio.NewScanner(log)
	scanner.Scan()

	last_time, err := time.Parse(TIME_FORMAT, scanner.Text())
	if err != nil {
		return time.Time{}, fmt.Errorf("last_success(): couldn't parse last request time: %v", err)
	}

	return last_time, nil
}

func update_last() error {

	log, err := os.Create(LAST_REQUEST_FILE)
	defer log.Close()
	if err != nil {
		return err
	}

	_, err = fmt.Fprintf(log, "%s\n", time.Now().UTC().Format(TIME_FORMAT))
	if err != nil {
		return err
	}

	return nil
}

func main() {
	last_time, err := last_success()
	if err != nil {
		fail(fmt.Sprintf("%v", err))
	} else if time.Now().UTC().Sub(last_time) < WAIT_TIME {
		refuse(last_time.Add(WAIT_TIME))
	} else {
		err = update_last()
		if err != nil {
			fail(fmt.Sprintf("%v", err))
		} else {
			succeed()
		}
	}
}
