import tarfile
import sys
import os.path

DISALLOWED_STARTS = ("/", "\\", "C:", "c:")

def fatalerror(msg):
	print(msg)
	print("Aborted. Press return to quit.")
	input()
	exit()

if len(sys.argv) != 2:
	print("len(sys.argv) == {}".format(len(sys.argv)))
	fatalerror("Usage: {0} <filename>".format(sys.argv[0]))

infilename = sys.argv[1]

outdir = sys.argv[1] + ".extracted"

if os.path.exists(outdir):
	fatalerror("Destination already exists!")

if not os.path.isfile(infilename):
	fatalerror("File \"{0}\" does not exist!".format(infilename))

if not tarfile.is_tarfile(infilename):
	fatalerror("File \"{0}\" is not a tarfile!".format(infilename))

infile = tarfile.open(infilename)

os.chdir(os.path.dirname(infilename))	# Set working dir to be same as infile.
dir = os.path.realpath(".")				# Make a note of working dir, for safety checks.

print("Working dir = {}".format(dir))
print("Output dir  = {}\n".format(outdir))

# Run safety checks: no moving upwards (..) or links (which could point outside the
# directory) or absolute paths. Also check for unusual item types.

# Absolute path checking is done by testing whether the real path of the item's name would
# be located in the current directory (or deeper) if it existed.

print("Inspecting contents:\n")
for item in infile:
	try:
		print(os.path.realpath(item.name)[len(dir):])
	except:
		print("<exception while printing>")
	if ".." in item.name:
		print("\nWARNING: Item contains \"..\"!")
		print("Allow? [yes/no]")
		if input() != "yes":
			fatalerror("User aborted.")
	if item.issym():
		fatalerror("Item {0} is a symbolic link!".format(item.name))
	if item.islnk():
		fatalerror("Item {0} is a hard link!".format(item.name))
	if (not item.isfile()) and (not item.isdir()):
		fatalerror("Item {0} is neither file nor directory!".format(item.name))

	# Check if the file's path would start with the current directory if it were extracted here...

	if not os.path.realpath(item.name).startswith(dir):
		fatalerror("Item {0} tries to extract outside current directory!".format(item.name))

	assert(not item.name.startswith(DISALLOWED_STARTS))		# This should have already been caught above, but safety first...

print("\nContents seem OK. Extracting...")
infile.extractall(outdir)
infile.close()
print("Done. Press return.")
input()
