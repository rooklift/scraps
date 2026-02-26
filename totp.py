import hmac
import hashlib
import struct
import time
import base64
import argparse


def main():

	parser = argparse.ArgumentParser(description = "Generate a TOTP code.")
	parser.add_argument("secret", nargs = "?", default = None, help = "Base32-encoded secret key")
	parser.add_argument("-i", "--interval", type = int, default = 30, help = "Time interval in seconds")
	args = parser.parse_args()

	interval = args.interval
	secret = args.secret

	if not secret:
		secret = input("Enter base32-encoded secret: ").strip()
		if not secret:
			print("No secret provided.")
			return

	loop(secret, interval)


def loop(secret, interval):
	while True:
		t = time.time()
		code = get_totp(secret, get_counter(t, interval))
		remaining = get_remaining_time(t, interval)
		print(f"{code}  (expires in {int(remaining)}s)")
		time.sleep(remaining + 0.5)


def get_counter(unix_seconds, interval):
	return int(unix_seconds) // interval


def get_remaining_time(unix_seconds, interval):
	return interval - (unix_seconds % interval)


def get_totp(secret, counter):
	key = base64.b32decode(secret, casefold = True)
	counter_bytes = struct.pack(">Q", counter)
	mac = hmac.new(key, counter_bytes, hashlib.sha1).digest()
	offset = mac[-1] & 0x0F
	code = struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF
	return str(code % 1_000_000).zfill(6)


if __name__ == "__main__":
	main()
