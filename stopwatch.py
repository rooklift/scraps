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
	print(time.monotonic() - start_time)

while True:
	timer()
