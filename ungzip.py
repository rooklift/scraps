import gzip
import sys

from pathlib import Path

infilenames = sys.argv[1:]
assert(infilenames)

for infilename in infilenames:

	if infilename[-3:] == ".gz" and len(infilename) > 3:
		outfilename = infilename[:-3]
	else:
		outfilename = infilename + ".extracted"

	f = gzip.open(infilename, 'rb')
	content = f.read()
	f.close()

	f = open(outfilename, 'wb')
	f.write(content)
	f.close()
