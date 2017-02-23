// Fairly trivial file emailer, but I needed this for work, hence it exists.

package main

import (
    "encoding/json"
    "fmt"
    "net/mail"
    "net/smtp"
    "os"

    "github.com/scorredoira/email"
)

const CONFIG_FILE = "file_emailer.cfg"

type Config struct {
    Recipient string    `json:"recipient"`
    Server string       `json:"server"`
    Port int            `json:"port"`
    FromName string     `json:"from_name"`
    FromEmail string    `json:"from_email"`
    Account string      `json:"account"`
    Password string     `json:"password"`
    Subject string      `json:"subject"`
    Files []string      `json:"files"`
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

    config, err := ParseConfig(CONFIG_FILE)
    if err != nil {
        fmt.Printf("%v\n", err)
        return
    }

    auth := smtp.PlainAuth("", config.Account, config.Password, config.Server)

    m := email.NewMessage(fmt.Sprintf("Report from %s", config.FromName), fmt.Sprintf("Your humble and obedient servant %s sends the following files...", config.FromName))
    m.From = mail.Address{Name: config.FromName, Address: config.FromEmail}
    m.To = []string{config.Recipient}

    for _, filename := range(config.Files) {
        err := m.Attach(filename)
        if err != nil {
            fmt.Printf("%v\n", err)
        }
    }

    err = email.Send(fmt.Sprintf("%s:%d", config.Server, config.Port), auth, m)
    if err != nil {
        fmt.Printf("%v\n", err)
    }
}
