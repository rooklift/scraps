// Fairly trivial file emailer. Configuration via .cfg file.
// We check the folder *unsent_dir* and send all files within
// to the specified recipient, then move all successfully-sent
// files to *sent_dir*.
//
// This is designed to be run as a cron job, really.

package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/mail"
    "net/smtp"
    "os"
    "path/filepath"

    "github.com/scorredoira/email"
)

const (
    CONFIG_FILE = "file_emailer2.cfg"
)

type Config struct {
    Recipients []string `json:"recipients"`
    Server string       `json:"server"`
    Port int            `json:"port"`
    FromName string     `json:"from_name"`
    FromEmail string    `json:"from_email"`
    Account string      `json:"account"`
    Password string     `json:"password"`
    Subject string      `json:"subject"`
    UnsentDir string    `json:"unsent_dir"`
    SentDir string      `json:"sent_dir"`
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

    var err error
    var attached_files []string

    config, err := ParseConfig(CONFIG_FILE)
    if err != nil {
        fmt.Printf("%v\n", err)
        return
    }

    auth := smtp.PlainAuth("", config.Account, config.Password, config.Server)

    m := email.NewMessage(fmt.Sprintf("Report from %s", config.FromName), fmt.Sprintf("Automatically generated email from %s...", config.FromName))
    m.From = mail.Address{Name: config.FromName, Address: config.FromEmail}
    m.To = config.Recipients

    unsent_files, err := ioutil.ReadDir(config.UnsentDir)
    if err != nil {
        fmt.Printf("%v\n", err)
        return
    }

    if len(unsent_files) == 0 {
        return
    }

    for _, fileinfo := range(unsent_files) {
        filename := fileinfo.Name()
        if fileinfo.IsDir() {
            fmt.Printf("%s was directory, skipping...\n", filename)
            continue
        }
        err = m.Attach(filepath.Join(config.UnsentDir, filename))
        if err != nil {
            fmt.Printf("%v\n", err)
            continue
        }
        attached_files = append(attached_files, filename)
    }

    err = email.Send(fmt.Sprintf("%s:%d", config.Server, config.Port), auth, m)
    if err != nil {
        fmt.Printf("%v\n", err)
        return
    }

    for _, filename := range(attached_files) {      // All these were successfully attached and sent...
        err = os.Rename(filepath.Join(config.UnsentDir, filename), filepath.Join(config.SentDir, filename))
        if err != nil {
            fmt.Printf("%v\n", err)
        }
    }
}
