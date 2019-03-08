package main

import (
	"encoding/json"
	"fmt"
	"net/mail"
	"net/smtp"
	"os"
	"strings"
	"time"

	"github.com/scorredoira/email"
)

const CONFIG_FILE = "file_emailer3.cfg"

type Config struct {
	Recipient string				`json:"recipient"`
	Server string					`json:"server"`
	Port int						`json:"port"`
	FromName string					`json:"from_name"`
	FromEmail string				`json:"from_email"`
	Account string					`json:"account"`
	Password string					`json:"password"`
	Subject string					`json:"subject"`
	Body string						`json:"body"`
	RetrySeconds time.Duration		`json:"retry_seconds"`
	TerminateSeconds time.Duration	`json:"terminate_seconds"`
	Files []string					`json:"files"`
}

func ParseConfig(filename string) (Config, error) {

	var ret Config

	infile, err := os.Open(filename)
	if infile != nil {
		defer infile.Close()
	}
	if err != nil {
		return ret, fmt.Errorf("ParseConfig(): %v", err)
	}

	decoder := json.NewDecoder(infile)
	err = decoder.Decode(&ret)
	if err != nil {
		return ret, fmt.Errorf("ParseConfig(): %v", err)
	}

	return ret, nil
}

func main() {

	start_time := time.Now()

	config, err := ParseConfig(CONFIG_FILE)
	if err != nil {
		fmt.Printf("%v\n", err)
		return
	}

	auth := smtp.PlainAuth("", config.Account, config.Password, config.Server)

	m := email.NewMessage(fmt.Sprintf("Report from %s", config.FromName), "")		// Body will be constructed later...
	m.From = mail.Address{Name: config.FromName, Address: config.FromEmail}
	m.To = []string{config.Recipient}

	var file_errors_flag bool

	for _, filename := range(config.Files) {
		err := m.Attach(filename)
		if err != nil {
			fmt.Printf("%v\n", err)
			file_errors_flag = true
		}
	}

	// Main send/retry loop...

	var send_errors []error

	for {

		// Construct the actual body...

		var msg_strings []string

		msg_strings = append(msg_strings, config.Body)

		if file_errors_flag {
			msg_strings = append(msg_strings, "WARNING: errors were encountered while attaching files. This usually means the files were not present.")
		}

		// Add all sending errors seen so far to the body...

		if len(send_errors) > 0 {

			msg_strings = append(msg_strings, fmt.Sprintf("This email succeeded after %d failed attempts. The following errors occurred during those attempts...", len(send_errors)))

			for _, e := range(send_errors) {
				msg_strings = append(msg_strings, e.Error())
			}
		}

		m.Body = strings.Join(msg_strings, "\r\n\r\n")

		// Try sending...

		err = email.Send(fmt.Sprintf("%s:%d", config.Server, config.Port), auth, m)
		if err == nil {
			os.Exit(0)
		} else {
			fmt.Printf("%v\n", err)
			send_errors = append(send_errors, err)
		}

		if time.Now().Sub(start_time) > config.TerminateSeconds * time.Second {
			os.Exit(0)
		}

		time.Sleep(config.RetrySeconds * time.Second)

	}
}
