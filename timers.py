# You have 2 simple sand timers.
# One contains 4 minutes of sand and the other contains 7.
# Is it possible to measure out 9 minutes?
#
# General-ish solution...

from itertools import combinations

class Timer:
	def __init__(self, top, bottom):
		self.top = top
		self.bottom = bottom
	def turn(self):
		self.top, self.bottom = self.bottom, self.top
	def copy(self):
		return Timer(self.top, self.bottom)
	def active(self):
		return self.top > 0
	def just_started(self):
		return self.bottom == 0
	def advance(self, n):
		self.bottom += min(n, self.top)
		if self.top < n:
			self.top = 0
		else:
			self.top -= n
	def __str__(self):
		return "({}|{})".format(self.top, self.bottom)


def advance_timers(timers):

	# Immediate return if nothing is happening:
	if not any(timer.active() for timer in timers):
		return 0

	sub_elapsed = 0
	reached_next = False
	while not reached_next:
		sub_elapsed += 1
		for timer in timers:
			if timer.active():
				timer.advance(1)
				if not timer.active():
					reached_next = True
	return sub_elapsed


def copy_timers(timers):
	return [timer.copy() for timer in timers]


def copy_history(history):
	return [n for n in history]


def index_combos(list_length):
	return [list(c) for r in range(list_length + 1) for c in combinations(range(list_length), r)]


def dfs(target, elapsed, history, timers):

	# Run time forward till the next decision point...

	elapsed += advance_timers(timers)

	if elapsed > target:
		return None

	if elapsed == target:
		return history

	all_options = index_combos(len(timers))

	for option in all_options:

		if len(option) == 0:
			if len(history) == 0 or len(history[-1]) == 0:
				continue
			if not any(timer.active() for timer in timers):
				continue

		ok = True

		for i in option:
			if timers[i].just_started():		# Is this even possible??
				ok = False
				break

		if ok:

			history_copy = copy_history(history)
			history_copy.append(option)

			timers_copy = copy_timers(timers)
			for i in option:
				timers_copy[i].turn()

			result = dfs(target, elapsed, history_copy, timers_copy)
			if result:
				return result

	return None


def solve(target, size_list):
	timers = [Timer(0, n) for n in size_list]
	print(dfs(target, 0, [], timers))



solve(9, [4, 7])
solve(15, [7, 11])
solve(13, [5, 9])
