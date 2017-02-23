import gzip
import sys

infilenames = sys.argv[1:]
assert(infilenames)

for infilename in infilenames:

	outfilename = infilename + ".extracted"

	f = gzip.open(infilename, 'rb')
	content = f.read()
	f.close()

	f = open(outfilename, 'wb')
	f.write(content)
	f.close()
