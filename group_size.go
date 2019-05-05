func (self *Board) GroupSizeAlt(p string) int {

	if self.GetState(p) == EMPTY {			// Use GetState not get_state_fast since we don't trust p yet.
		return 0
	}

	colour := self.get_state_fast(p)

	TOUCHED := Colour(127)

	self.set_state_fast(p, TOUCHED)
	count := 1

	todo := []string{p}
	tofix := []string{p}
	next := []string{}

	for len(todo) > 0 {
		for _, p := range todo {
			for _, a := range AdjacentPoints(p, self.Size) {
				if self.get_state_fast(a) == colour {
					count++
					next = append(next, a)
					self.set_state_fast(a, TOUCHED)
					tofix = append(tofix, a)
				}
			}
		}

		todo = next
		next = nil
	}

	for _, p := range tofix {
		self.set_state_fast(p, colour)
	}

	return count
}
