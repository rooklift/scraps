import subprocess, threading, queue, time

p = subprocess.Popen("C:\\Programs (self-installed)\\Chess Engines\\stockfish_15_x64_avx2.exe",
	stdin = subprocess.PIPE,
	stdout = subprocess.PIPE,
	stderr = subprocess.DEVNULL)

incoming_queue = queue.Queue()

def send(s):
	p.stdin.write(s.encode("utf8"))
	p.stdin.flush()

def receive_thread():
	while True:
		incoming_queue.put(p.stdout.readline().decode("utf8"))

threading.Thread(target = receive_thread, daemon = True).start()

send("uci\n")

while True:
	try:
		msg = incoming_queue.get(block = False)
		print(msg, end="")
	except queue.Empty:
		time.sleep(0.1)
