import os

prefixes = []		# FIXME - add prefixes
errors = False

def handle_folder(folder):
	global errors
	for f in os.listdir(folder):
		fullpath = os.path.join(folder, f)
		if os.path.isdir(fullpath):
			handle_folder(fullpath)
		else:
			for prefix in prefixes:
				if f.startswith(prefix):
					newpath = os.path.join(folder, f.removeprefix(prefix))
					try:
						os.rename(fullpath, newpath)
						print(newpath)
					except Exception as e:
						print(e)
						errors = True

def main():
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	handle_folder(".")
	if errors:
		input()

main()
