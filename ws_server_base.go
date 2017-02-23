package main

import (
    "fmt"
    "net/http"
    "sync"
    "time"

    "github.com/gorilla/websocket"
)

const SERVER = "127.0.0.1:8000"

var Upgrader = websocket.Upgrader{ReadBufferSize: 1024, WriteBufferSize: 1024, CheckOrigin: func(r *http.Request) bool {return true}}

var AllMsgChannels []chan string    // List of all channels down which we send simulator messages (one per open websocket connection)
var AllMsgChannels_MUTEX sync.Mutex

func main() {
    go simulator()
    http.HandleFunc("/ws/", ws_handler)
    http.ListenAndServe(SERVER, nil)
}

func ws_handler(writer http.ResponseWriter, request * http.Request) {

    conn, err := Upgrader.Upgrade(writer, request, nil)
    if err != nil {
        return
    }

    our_msg_channel := make(chan string)

    AllMsgChannels_MUTEX.Lock()
    AllMsgChannels = append(AllMsgChannels, our_msg_channel)
    AllMsgChannels_MUTEX.Unlock()

    go ws_reader(conn, our_msg_channel)

    for {
        msg := <- our_msg_channel
        err = conn.WriteMessage(websocket.TextMessage, []byte(msg))
        if err != nil {
            remove_msg_chan(our_msg_channel)
            return
        }
    }

    return
}

func ws_reader(conn * websocket.Conn, our_msg_channel chan string) {
    for {
        if _, _, err := conn.NextReader(); err != nil {
            remove_msg_chan(our_msg_channel)
            conn.Close()
            return
        }
    }
}

func remove_msg_chan(msg_channel chan string) {

    AllMsgChannels_MUTEX.Lock()
    defer AllMsgChannels_MUTEX.Unlock()

    for i, channel := range AllMsgChannels {
        if channel == msg_channel {
            AllMsgChannels[i] = AllMsgChannels[len(AllMsgChannels) - 1]
            AllMsgChannels = AllMsgChannels[:len(AllMsgChannels) - 1]
            break
        }
    }
}

// --------------------------------------------------------

func simulator() {

    var sim Sim

    ticker := time.Tick(time.Second / 60)

    for {
        <- ticker

        AllMsgChannels_MUTEX.Lock()
        length := len(AllMsgChannels)
        AllMsgChannels_MUTEX.Unlock()

        if length > 0 {     // No simulation without representation!
            msg := sim.iterate()
            AllMsgChannels_MUTEX.Lock()
            for _, msg_channel := range AllMsgChannels {
                msg_channel <- msg
            }
            AllMsgChannels_MUTEX.Unlock()
        }
    }
}

// --------------------------------------------------------

type Sim struct {
    i int
}

func (s *Sim) iterate()  string {
    s.i += 1
    return fmt.Sprintf("%d", s.i)
}
