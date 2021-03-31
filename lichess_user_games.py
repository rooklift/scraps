import requests

username = input("Username for download? ")
token = input("Your API token? ")

headers = {"Authorization": f"Bearer {token}"}

r = requests.get(f"https://lichess.org/api/games/user/{username}", headers = headers, stream = True)

if r.encoding is None:
	r.encoding = "utf8"

with open(f"{username}_lichess.pgn", "w") as outfile:
	for line in r.iter_lines(decode_unicode = True):
		outfile.write(line)
		outfile.write("\n")

