import tarfile
import sys
import os.path

def fatalerror(msg):
	print(msg)
	print("Aborted. Press return to exit.")
	input()
	exit()

if len(sys.argv) != 2:
	print("len(sys.argv) == {}".format(len(sys.argv)))
	fatalerror("Usage: {0} <filename>".format(sys.argv[0]))

if not os.path.exists(sys.argv[1]):
	fatalerror("\"{0}\" does not exist!".format(sys.argv[1]))

outfilename = sys.argv[1] + ".tar.gz"

if os.path.exists(outfilename):
	fatalerror("{} already exists!".format(outfilename))

outfile = tarfile.open(name=outfilename, mode='w:gz')
outfile.add(name = sys.argv[1], arcname = os.path.basename(sys.argv[1]))
								# This sets the name of the thing in the archive to just have its final
								# part of its name i.e. "C:/foo/bar/blah" just gets named "blah"
outfile.close()
