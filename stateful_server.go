package main

// Is this the best way to do this?
//
// The ServeHTTP() method needs to be called on an object,
// not a pointer to the object, so it always gets a copy of
// the server object, meaning the server object needs to
// contain a pointer to the real data, right?

import (
	"fmt"
	"net/http"
)

type server struct {
	storage *server_storage
}

type server_storage struct {
	hits int
}

func NewServer() server {
	var s server
	s.storage = new(server_storage)
	return s
}

func (s server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	s.storage.hits += 1
	fmt.Fprintf(w, "Hits: %d", s.storage.hits)
}

func main() {
	s := NewServer()
	http.ListenAndServe("localhost:8000", s)
}
