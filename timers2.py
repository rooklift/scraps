# You have 2 simple sand timers.
# One contains 4 minutes of sand and the other contains 7.
# Is it possible to measure out 9 minutes?
#
# General-ish solution...
#
# State is tuple like so:
#	(target, elapsed, (top, bottom), (top, bottom) ...)
#	So timers are in positions [2:]
#	Number of timers is len(foo) - 2

from itertools import combinations


def index_combos(list_length):
	return [list(c) for r in range(list_length + 1) for c in combinations(range(list_length), r)]


def is_solution(state):
	return state[0] == state[1]


def is_dead_end(state):
	return state[0] < state[1]


def get_possible_moves(state):

	timers = state[2:]
	combos = index_combos(len(timers))			# e.g. [ [], [0], [1], [0, 1] ]

	ret = []

	for option in combos:
		if len(option) == 0:					# Don't use this (continue) if no timer is active.
			if any(timer[0] > 0 for timer in timers):
				ret.append(option)
		else:
			ret.append(option)

	return ret


def apply_move(state, move):					# A move is a list of indices to flip where 0 means the first timer, which is offset by 2 in the state tuple.

	target = state[0]
	elapsed = state[1]
	timers = [list(timer) for timer in state[2:]]					# Mutable

	for i in move:
		timers[i][0], timers[i][1] = timers[i][1], timers[i][0]		# Flip

	# How long until a timer runs out?

	runtime = min([timer[0] for timer in timers if timer[0] > 0])	# Will throw if no timer has anything up top, but that should be impossible.

	for timer in timers:
		if timer[0] < runtime:					# Not much left on top (possibly zero)
			timer[1] += timer[0]				# Send it all to the bottom
			timer[0] = 0						# All gone from top
		else:
			timer[1] += runtime
			timer[0] -= runtime

	timers = [tuple(timer) for timer in timers]

	return (target, elapsed + runtime) + tuple(timers)


def dfs(state, seen = None):

	if seen is None:
		seen = set()

	if state in seen:
		return None

	seen.add(state)

	if is_solution(state):
		return []

	if is_dead_end(state):
		return None

	for move in get_possible_moves(state):
		next_state = apply_move(state, move)
		result = dfs(next_state, seen)
		if result is not None:
			return [move] + result

	return None


def solve(target, durations):
	state = (target, 0)
	for d in durations:
		state += ((0, d),)
	print(dfs(state))


def main():
	solve(9, [4, 7])
	solve(15, [7, 11])
	solve(13, [5, 9])


main()
