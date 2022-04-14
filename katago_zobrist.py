import json, subprocess, threading, time

# -------------------------------------------------------------------------------------------------
# Dealing with the KataGo process...

exe_path = "C:\\Programs (self-installed)\\KataGo 1.11.0 OpenCL\\katago.exe"

args = [
	"analysis",
	"-config",
	"C:\\Programs (self-installed)\\KataGo 1.11.0 OpenCL\\analysis_example.cfg",
	"-model",
	"C:\\Users\\Owner\\Documents\\Misc\\KataGo\\kata1-b40c256-s11101799168-d2715431527.bin.gz",
	"-quit-without-waiting"]

p = subprocess.Popen(
	[exe_path] + args,
	stdin = subprocess.PIPE,
	stdout = subprocess.PIPE,
	stderr = subprocess.DEVNULL)

def send(o):
	s = json.dumps(o) + "\n"
	p.stdin.write(s.encode("utf8"))
	p.stdin.flush()

def send_query(id_string, stones, player):

	assert(type(id_string) is str)
	assert(type(stones) is list)
	assert(player in ["B", "W"])
	
	d = {
		"id": id_string,
		"moves": [],
		"rules": "Chinese",
		"komi": 7.5,
		"boardXSize": 19,
		"boardYSize": 19,
		"initialStones": stones,
		"initialPlayer": player,
		"maxVisits": 1,
	}

	send(d)

def receive_and_extract_hash():
	kata_output = p.stdout.readline().decode("utf8")
	d = json.loads(kata_output)
	return int(d["rootInfo"]["thisHash"], base=16)

# -------------------------------------------------------------------------------------------------
# Utility...

def xy_to_gtp(x, y):
	x_ascii = x + 65
	if x_ascii >= ord("I"):
		x_ascii += 1
	y = 19 - y
	return chr(x_ascii) + str(y)

def nice_hex(i):
	s = hex(i)[2:]			# remove the 0x
	while len(s) < 32:
		s = "0" + s
	return "0x" + s + "n"	# restore the 0x, add JS bigint marker

# -------------------------------------------------------------------------------------------------

send_query("b_19x19", [], "B")
b_19x19 = receive_and_extract_hash()

send_query("w_19x19", [], "W")
w_19x19 = receive_and_extract_hash()

for stone_colour in ["B", "W"]:

	print()
	print("{} STONES...".format(stone_colour))

	done = 0

	for y in range(19):
		for x in range(19):
			stones = [[stone_colour, xy_to_gtp(x, y)]]
			send_query("{},{}".format(x, y), stones, "B")		# Always Black to play...
			h = receive_and_extract_hash() ^ b_19x19			# XOR against the empty position to get what difference this stone made.
			print(nice_hex(h) + ", ", end="")
			done += 1
			if (done % 3 == 0):
				print()


print()
print("B TO PLAY...")
print(nice_hex(b_19x19))

print("W TO PLAY...")
print(nice_hex(w_19x19))
