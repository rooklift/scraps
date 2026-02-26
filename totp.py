import argparse, base64, hashlib, hmac, time


def main():

	parser = argparse.ArgumentParser(description = "Generate a TOTP code.")
	parser.add_argument("secret", nargs = "?", default = None, help = "Base32-encoded secret key")
	parser.add_argument("-i", "--interval", type = int, default = 30, help = "Time interval in seconds")
	parser.add_argument("-d", "--digits", type = int, default = 6, help = "Number of digits needed")
	args = parser.parse_args()

	interval = args.interval
	secret = args.secret
	digits = args.digits

	if not secret:
		secret = input("Enter base32-encoded secret: ").strip()
		if not secret:
			print("No secret provided.")
			return

	loop(secret, interval, digits)


def loop(secret, interval, digits):
	while True:
		t = time.time()
		code = get_totp(secret, get_counter(t, interval))
		remaining = get_remaining_time(t, interval)
		print(f"{display_code(code, digits)}  (expires in {int(remaining)}s)")
		time.sleep(remaining + 0.5)


def get_totp(secret, counter):
	key = base64.b32decode(secret, casefold = True)
	mac = hmac.new(key, int_as_8_bytes(counter), hashlib.sha1).digest()
	return extract_totp_from_digest(mac)


def extract_totp_from_digest(dig):
	assert(len(dig) == 20)
	offset = dig[-1] & 0x0f													# Last nibble determines where to read.
	return bytes_to_int(dig[offset : offset + 4]) & 0x7fffffff				# Spec says screen-out sign-bit.


def get_counter(unix_seconds, interval):
	return int(unix_seconds) // interval


def get_remaining_time(unix_seconds, interval):
	return interval - (unix_seconds % interval)


def int_as_8_bytes(n):														# Big-endian. Could use struct.pack(">Q", n) for this.
	ret = bytearray(8)
	for i in range(8):
		foo = n >> ((7 - i) * 8)
		foo &= 0xff
		ret[i] = foo
	return bytes(ret)


def bytes_to_int(b):														# Big-endian. Could use int.from_bytes(b, "big") for this.
	ret = 0
	for by in b:
		ret *= 256
		ret += by
	return ret


def display_code(code, digits):
	ret = str(code)[-digits:]
	while len(ret) < digits:
		ret = "0" + ret
	return ret


# -------------------------------------------------------------------------------------------------

if __name__ == "__main__":
	main()

# -------------------------------------------------------------------------------------------------

def test():

	test_vectors = {
		59:          "94287082",
		1111111109:  "07081804",
		1111111111:  "14050471",
		1234567890:  "89005924",
		2000000000:  "69279037",
		20000000000: "65353130",
	}

	test_key = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"

	test_interval = 30

	test_digits = 8

	for t, expect in test_vectors.items():
		code = get_totp(test_key, get_counter(t, test_interval))
		s = display_code(code, test_digits)
		print(f"{t:>12}: {expect}, {'pass' if s == expect else 'FAIL'}")
