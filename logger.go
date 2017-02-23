package logger

import (
    "fmt"
    "os"
)

type Logfile struct {
    outfile         *os.File
    outfilename     string
    enabled         bool
}

func NewLog(outfilename string, enabled bool) *Logfile {
    return &Logfile{nil, outfilename, enabled}
}

func (log *Logfile) Dump(format_string string, args ...interface{}) {

    if log.enabled == false {
        return
    }

    if log.outfile == nil {

        var err error

        if _, tmp_err := os.Stat(log.outfilename); tmp_err == nil {         // File exists
            log.outfile, err = os.OpenFile(log.outfilename, os.O_APPEND|os.O_WRONLY, 0666)
        } else {                                                            // File needs creating
            log.outfile, err = os.Create(log.outfilename)
        }

        if err != nil {
            log.enabled = false
            return
        }
    }

    fmt.Fprintf(log.outfile, format_string, args...)
    fmt.Fprintf(log.outfile, "\n")
}
