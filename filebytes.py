import sys

COUNT = 256

def printable(byte):
	s = hex(byte)[2:]		# remove 0x
	if len(s) == 1:
		s = "0" + s
	return s


with open(sys.argv[1], "rb") as infile:
	fbytes = infile.read(COUNT)

print()

for i, byte in enumerate(fbytes):
	print(" " + printable(byte), end="")
	if (i % 16 == 15):
		print()



input()
