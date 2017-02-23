package main

// This is a very specific web-crawler designed to archive a particular blog.
// The URL however is redacted here.

import (
    "bytes"
    "fmt"
    "io/ioutil"
    "net/http"
    "os"
    "strings"
    "time"
)

const (
    FIRST_PAGE = "REDACTED"     // actually the LAST entry in the blog; we crawl backwards in time
    NEXT_URL_SEARCH = "<div class='social-links' style='text-align: center'><a href=\""
    MAX_FAILS_IN_A_ROW = 2
)

func main() {

    url := FIRST_PAGE
    first_loop := true
    fails_in_a_row := 0

    for {

        if fails_in_a_row > MAX_FAILS_IN_A_ROW {
            fmt.Printf("Failed %d times in a row, quitting...\n", fails_in_a_row)
            os.Exit(1)
        }

        if first_loop == false {
            time.Sleep(20 * time.Second)
        } else {
            first_loop = false
        }

        fmt.Printf("Get: %s\n", url)

        resp, err := http.Get(url)
        if err != nil {
            fmt.Printf("Failed to get %s ... %v\n", url, err)
            fails_in_a_row += 1
            continue
        }

        body, err := ioutil.ReadAll(resp.Body)
        if err != nil {
            fmt.Printf("Failed to get %s ... %v\n", url, err)
            fails_in_a_row += 1
            continue
        }

        resp.Body.Close()
        fails_in_a_row = 0

        err = write_to_file(body, filename_from_url(url))
        if err != nil {
            fmt.Printf("%v\n", err)
            os.Exit(1)
        }

        url, err = find_next_url(body)
        if err != nil {
            fmt.Printf("%v\n", err)
            os.Exit(1)
        }
    }
}

func write_to_file(body []byte, filename string) error {

    outfile, err := os.Create(filename)
    if err != nil {
        return fmt.Errorf("write_to_file() failed to create %s ... %v", filename, err)
    }
    outfile.Write(body)
    outfile.Close()
    return nil
}

func find_next_url(body []byte) (string, error) {

    search_string := []byte(NEXT_URL_SEARCH)
    index := bytes.Index(body, search_string)
    if index == -1 {
        return "", fmt.Errorf("find_next_url() failed to find search string")
    }
    index += len(search_string)

    // With the index now pointing at the first character in the a href="whatever" read until reaching a new "
    //                                        i.e. index now points here ^

    var result []byte

    for {
        if body[index] == '"' {
            break
        }
        result = append(result, body[index])
        index++
    }

    return string(result), nil
}

func filename_from_url(url string) string {

    // convert: "http://foo.com/118172.html" --> "118172.html"

    index := strings.LastIndex(url, "/")
    index += 1      // Don't include the / in the result

    return url[index:]
}
