package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"net/http"
)

type Player struct {
	Name			string		`json:name`
}

type GameState struct {
	Moves			string		`json:moves`
	Wtime			int			`json:wtime`
	Btime			int			`json:btime`
	Winc			int			`json:winc`
	Binc			int			`json:binc`
}

type GameEvent struct {			// Can be of many types - may actually be a GameState
	Type			string		`json:type`
	Id				string		`json:id`
	White			Player		`json:white`
	Black			Player		`json:black`
	Moves			string		`json:moves`
	Wtime			int			`json:wtime`
	Btime			int			`json:btime`
	Winc			int			`json:winc`
	Binc			int			`json:binc`
	State			GameState	`json:state`
}

type Game struct {
	Resp			*http.Response
	Reader			*bufio.Reader
}

func (self *Game) Init(gameId string) error {

	resp, err := http.Get(fmt.Sprintf("https://lichess.org/api/bot/game/stream/%s", gameId))

	self.Resp = resp

	if err != nil {
		return err
	}

	self.Reader = bufio.NewReader(self.Resp.Body)

	return nil
}

func (self *Game) GetNextEvent() (*GameEvent, error) {

	for {
		line, err := self.Reader.ReadBytes('\n')
		if err != nil {
			return nil, err
		}

		ev := new(GameEvent)

		err = json.Unmarshal(line, ev)
		if err != nil {
			return nil, err
		}

		return ev, nil
	}
}

func main() {
	return
}
