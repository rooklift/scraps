#!/usr/bin/env python3

import json, os.path, sqlite3, sys
import go_db

# This takes as argument the output of github.com/fohristiwhirl/sgf/summaries.go
# Not really necessary since I sped up gofish

def main():

	conn = sqlite3.connect('go.db')
	c = conn.cursor()
	c.execute(
		'''
				CREATE TABLE Games (
					path text,
					filename text,
					dyer text,
					SZ int,
					HA int,
					PB text,
					PW text,
					BR text,
					WR text,
					RE text,
					DT text,
					EV text);
		''')

	n = 0

	with open(sys.argv[1]) as infile:
		for s in infile:
			if "{" in s:
				o = json.loads(s)
				r = go_db.Record(**o)
				go_db.add_game_to_db(r, c)
				n += 1

	print("Added {} records".format(n))

	conn.commit()
	c.close()
	input()


if __name__ == "__main__":
	main()
