import hmac
import hashlib
import struct
import time
import base64

SECRET = ""  # Base32-encoded secret, should be set on first use.

def get_totp(secret, interval=30):
	key = base64.b32decode(secret, casefold=True)
	counter = int(time.time()) // interval
	counter_bytes = struct.pack(">Q", counter)
	mac = hmac.new(key, counter_bytes, hashlib.sha1).digest()
	offset = mac[-1] & 0x0F
	code = struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF
	return str(code % 1_000_000).zfill(6)

if __name__ == "__main__":
	code = get_totp(SECRET)
	seconds_left = 30 - (int(time.time()) % 30)
	print(f"{code}  (expires in {seconds_left}s)")
	input()
