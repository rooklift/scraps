import hmac
import hashlib
import struct
import time
import base64
import argparse

def get_totp(secret, interval):
	key = base64.b32decode(secret, casefold=True)
	counter = int(time.time()) // interval
	counter_bytes = struct.pack(">Q", counter)
	mac = hmac.new(key, counter_bytes, hashlib.sha1).digest()
	offset = mac[-1] & 0x0F
	code = struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF
	return str(code % 1_000_000).zfill(6)

def main():

	parser = argparse.ArgumentParser(description="Generate a TOTP code.")
	parser.add_argument("secret", nargs="?", default=None, help="Base32-encoded secret key")
	parser.add_argument("-i", "--interval", type=int, default=30, help=f"Time interval in seconds")
	args = parser.parse_args()

	secret = args.secret
	if not secret:
		secret = input("Enter base32-encoded secret: ").strip()
		if not secret:
			print("No secret provided.")
			return

	while True:
		code = get_totp(secret, args.interval)
		seconds_left = args.interval - (int(time.time()) % args.interval)
		print(f"{code}  (expires in {seconds_left}s)")
		time.sleep(seconds_left + 2)

if __name__ == "__main__":
	main()
