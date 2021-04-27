import os

OUTFILENAME = "output.txt"

files = [f for f in os.listdir(".") if os.path.isfile(f) and f != os.path.basename(__file__) and f != OUTFILENAME]

strings = []

for f in files:
	with open(f) as infile:
		strings.append(infile.read())

with open("output.txt", "w") as outfile:
	outfile.write("\n".join(strings))
