import hashlib
import sys
import os.path

if len(sys.argv) == 1:
	print("Usage: {} <filenames>".format(os.path.basename(sys.argv[0])))
else:
	for arg in sys.argv[1:]:
		try:
			infile = open(arg, "rb")
		except:
			print("Error opening file {}".format(arg))
			print()
			continue
		print(arg)
		file_contents = infile.read()
		s = hashlib.sha1()
		s.update(file_contents)
		print(" SHA-1: " + s.hexdigest())
		m = hashlib.md5()
		m.update(file_contents)
		print("   MD5: " + m.hexdigest())
		print()
		infile.close()

input()
