// Comparing insertion time for linked-list vs array (well, slice)

package main

import (
    "fmt"
    "time"
)

const (
    ELEMENTS = 100000000
    INSERT_POINT = 50000000
)

type Node struct {
    Previous    *Node
    Next        *Node
    Value       int32
}

type LinkedList struct {
    Root        *Node
}

func (ll *LinkedList) get(i int32) int32 {
    node := ll.Root
    for n := int32(0) ; n < i ; n++ {
        node = node.Next
    }
    return node.Value
}

func (ll *LinkedList) insert(i, v int32) {

    // FIXME if this was real: accept nil pointer, and accept ll with nil root

    var earlier_node *Node = nil
    var later_node *Node = ll.Root

    for n := int32(0) ; n < i ; n++ {
        earlier_node = later_node
        later_node = later_node.Next
    }

    new_node := new(Node)
    new_node.Value = v

    new_node.Previous = earlier_node
    new_node.Next = later_node

    if earlier_node != nil {
        earlier_node.Next = new_node
    }

    if later_node != nil {
        later_node.Previous = new_node
    }

    if i == 0 {
        ll.Root = new_node
    }

    return
}

func ll_buildup(elements int32) *LinkedList {

    current_node := new(Node)
    root := current_node

    for n := int32(1) ; n < elements ; n++ {
        next_node := new(Node)
        next_node.Previous = current_node
        next_node.Value = n
        current_node.Next = next_node
        current_node = next_node
    }

    ll := new(LinkedList)
    ll.Root = root

    return ll
}

func slice_buildup(elements, capacity int32) []int32 {

    s := make([]int32, elements, capacity)

    for n := int32(0) ; n < elements ; n++ {
        s[n] = n
    }

    return s
}

func main() {

    start := time.Now()
    linked_list := ll_buildup(ELEMENTS)
    end := time.Now()

    fmt.Printf("Time for LL buildup: %v\n", end.Sub(start))

    // ------------------------------------------------

    start = time.Now()
    linked_list.insert(INSERT_POINT, 1234)
    end = time.Now()

    fmt.Printf("Time for an LL insert: %v\n", end.Sub(start))

    // ------------------------------------------------

    start = time.Now()
    linked_list.get(INSERT_POINT)
    end = time.Now()

    fmt.Printf("Time for an LL get: %v\n", end.Sub(start))

    // ------------------------------------------------

    start = time.Now()
    slice := slice_buildup(ELEMENTS, ELEMENTS)      // capacity == len, meaning the first insertion will require a resize
    end = time.Now()

    fmt.Printf("Time for slice buildup: %v\n", end.Sub(start))

    // ------------------------------------------------

    start = time.Now()
    slice = append(slice, 0)
    copy(slice[INSERT_POINT+1:], slice[INSERT_POINT:])
    slice[INSERT_POINT] = 1234
    end = time.Now()

    fmt.Printf("Time for a slice insert with slice resize: %v\n", end.Sub(start))

    // ------------------------------------------------

    start = time.Now()
    slice = append(slice, 0)
    copy(slice[INSERT_POINT+1:], slice[INSERT_POINT:])
    slice[INSERT_POINT] = 1234
    end = time.Now()

    fmt.Printf("Time for a slice insert without slice resize: %v\n", end.Sub(start))
}
