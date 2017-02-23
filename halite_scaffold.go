package main

import (
    "bufio"
    "fmt"
    "os"
    "strconv"
    "strings"
)

const (
    NAME = "bot_name_here"

    STILL = 0
    NORTH = 1
    UP = 1
    EAST = 2
    RIGHT = 2
    SOUTH = 3
    DOWN = 3
    WEST = 4
    LEFT = 4
)

var scanner *bufio.Scanner

func init() {
    scanner = bufio.NewScanner(os.Stdin)
}

type Game struct {
    Id              int
    Width           int
    Height          int
    Size            int
    Production      []int
    Owner           []int
    Strength        []int
}

func (g *Game) ParseProduction() {
    scanner.Scan()
    production_fields := strings.Fields(scanner.Text())
    for i := 0; i < len(production_fields); i++ {
        g.Production[i], _ = strconv.Atoi(production_fields[i])
    }
}

func (g *Game) ParseMap() {

    // https://halite.io/advanced_writing_sp.php

    scanner.Scan()
    map_fields := strings.Fields(scanner.Text())

    field_index := 0

    game_index := 0
    for game_index < g.Size {

        num, _ := strconv.Atoi(map_fields[field_index])
        owner, _ := strconv.Atoi(map_fields[field_index + 1])
        field_index += 2

        for n := 0 ; n < num ; n++ {
            g.Owner[game_index] = owner
            game_index++
        }
    }

    game_index = 0
    for game_index < g.Size {
        g.Strength[game_index], _ = strconv.Atoi(map_fields[field_index])
        field_index++
        game_index++
    }
}

func (g *Game) Startup() {

    // Get our own ID

    scanner.Scan()
    g.Id, _ = strconv.Atoi(scanner.Text())

    // Get width and height

    scanner.Scan()
    width_and_height := strings.Fields(scanner.Text())
    g.Width, _ = strconv.Atoi(width_and_height[0])
    g.Height, _ = strconv.Atoi(width_and_height[1])
    g.Size = g.Width * g.Height

    // At this point we initialise correct size slices for the game state

    g.Production = make([]int, g.Size, g.Size)
    g.Owner = make([]int, g.Size, g.Size)
    g.Strength = make([]int, g.Size, g.Size)

    // Now parse initial game state

    g.ParseProduction()
    g.ParseMap()

    fmt.Printf("%s\n", NAME)
}

func (g *Game) I_to_XY(i int) (int, int) {
    x := i % g.Width
    y := i / g.Width
    return x, y
}

func (g *Game) XY_to_I(x, y int) (int) {

    if x < 0 {
        x += -(x / g.Width) * g.Width + g.Width      // Can make x == g.Width, so must still use % later
    }

    x %= g.Width

    if y < 0 {
        y += -(y / g.Height) * g.Height + g.Height   // Can make y == g.Height, so must still use % later
    }

    y %= g.Height

    return y * g.Width + x
}

func (g *Game) Play() {

    g.ParseMap()

    // MAIN LOGIC HERE, CHOOSE YOUR MOVES AND PRINT THEM TO STDOUT!

    fmt.Printf("\n")
}

func main() {
    g := new(Game)
    g.Startup()

    for {
        g.Play()
    }
}
