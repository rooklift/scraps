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

		h = hashlib.md5()
		h.update(file_contents)
		print("     MD5: " + h.hexdigest())

		h = hashlib.sha1()
		h.update(file_contents)
		print("   SHA-1: " + h.hexdigest())

		h = hashlib.sha256()
		h.update(file_contents)
		print(" SHA-256: " + h.hexdigest())

		h = hashlib.sha512()
		h.update(file_contents)
		s = h.hexdigest()
		print(" SHA-512: " + s[:len(s) // 2])
		print("          " + s[len(s) // 2:])

		print()
		infile.close()

input()
