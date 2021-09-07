import os

OUTFILENAME = "output.txt"

files = [f for f in os.listdir(".") if os.path.isfile(f) and f != os.path.basename(__file__) and f != OUTFILENAME]

bytearrays = []

for f in files:
	with open(f, "rb") as infile:
		bytearrays.append(infile.read())

with open("output.txt", "wb") as outfile:
	for ba in bytearrays:
		outfile.write(ba)
		outfile.write(b"\n\n")
