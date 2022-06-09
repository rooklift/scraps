package main

import (
	"bufio"
	"io"
	"os"
	"os/exec"
	"time"
)

const REAL_PROGRAM = "C:\\Programs (self-installed)\\Chess Engines\\stockfish_15_x64_avx2.exe"

const DELAY = 1 * time.Second					// How long to wait before relaying a message
const TICKRATE = 100 * time.Millisecond			// How often to flush relayed messages

type timed_message struct {
	t			time.Time						// Time the message came in
	msg			[]byte							// The message
	writer		io.Writer						// Where to write it to
}

func main() {

	exec_command := exec.Command(REAL_PROGRAM, os.Args[1:]...)
	i_pipe, _ := exec_command.StdinPipe()
	o_pipe, _ := exec_command.StdoutPipe()
	e_pipe, _ := exec_command.StderrPipe()
	exec_command.Start()

	relay_chan := make(chan timed_message, 128)

	go mitm(os.Stdin, i_pipe)
	go delayed_mitm(e_pipe, os.Stderr, relay_chan)
	go delayed_mitm(o_pipe, os.Stdout, relay_chan)
	relay(relay_chan)
}

func mitm(input io.Reader, output io.Writer) {
	scanner := bufio.NewScanner(input)
	for scanner.Scan() {
		output.Write(scanner.Bytes())
		output.Write([]byte{'\n'})
	}
}

func delayed_mitm(input io.Reader, output io.Writer, relay_chan chan timed_message) {
	scanner := bufio.NewScanner(input)
	for scanner.Scan() {
		relay_chan <- timed_message{t: time.Now(), msg: scanner.Bytes(), writer: output}
	}
}

func relay(relay_chan chan timed_message) {
	var messages []timed_message
	ticker := time.NewTicker(TICKRATE)
	for {
		select {
		case timedmsg := <- relay_chan:
			messages = append(messages, timedmsg)
		case <- ticker.C:
			messages_sent := 0
			for _, timedmsg := range messages {
				if time.Now().Sub(timedmsg.t) > DELAY {
					timedmsg.writer.Write(timedmsg.msg)
					timedmsg.writer.Write([]byte{'\n'})
					messages_sent++
				} else {
					break
				}
			}
			if messages_sent > 0 {
				messages = messages[messages_sent:]			// Does this lead to some backing array expanding forever?
			}
		}
	}
}
