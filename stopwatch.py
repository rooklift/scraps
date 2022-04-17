import queue, threading, time

end_notifier_queue = queue.Queue()

def get_stop_input():
	input("Press enter to stop")
	end_notifier_queue.put(True)

def timer():
	input("Press enter to begin")
	threading.Thread(target = get_stop_input).start()
	start_time = time.monotonic()
	while True:
		try:
			end_notifier_queue.get(block=False)
			break
		except:
			time.sleep(0.1)
	elapsed = time.monotonic() - start_time
	minutes = int(elapsed / 60)
	seconds = int(elapsed) % 60
	hundredths = int((elapsed - int(elapsed)) * 100)
	print("{:02}:{:02}.{:02}".format(minutes, seconds, hundredths))

while True:
	timer()
