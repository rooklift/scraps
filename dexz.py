# Open and extract .xz files

import lzma, sys
with lzma.open(sys.argv[1], "rb") as f:
    file_content = f.read()

ouffilename = sys.argv[1] + ".extracted"

outfile = open(ouffilename, "wb")
outfile.write(file_content)
