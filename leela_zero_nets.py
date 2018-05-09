import os, re, requests

pattern = re.compile(r"<a href=\"(.+)\">.+<\/a>\s+(..)-(...)-(....)\s+(..:..)\s+(\d+)")

months = {
	"Jan" : "01",
	"Feb" : "02",
	"Mar" : "03",
	"Apr" : "04",
	"May" : "05",
	"Jun" : "06",
	"Jul" : "07",
	"Aug" : "08",
	"Sep" : "09",
	"Oct" : "10",
	"Nov" : "11",
	"Dec" : "12",
}

nets = []

r = requests.get("http://storage.sjeng.org/networks/")
lines = r.text.split("\n")

for line in lines:

	try:
		filename, day, month, year, time, size = re.search(pattern, line).group(1, 2, 3, 4, 5, 6)
		date_fixed = year + months[month] + day + time[0:2] + time[3:5]
		nets.append([filename, date_fixed, size])

	except AttributeError:
		pass

nets.sort(key = lambda x : x[1])

for i, net in enumerate(nets):
	print("{0:>3}:  {1:>67}  {2}  {3}".format(i, net[0], net[1], net[2]))

while 1:

	s = input("Download item index? (0-{}) ".format(len(nets) - 1))

	if len(s) == 0:
		continue

	try:
		n = int(s)
	except:
		continue

	if n < 0 or n >= len(nets):
		continue

	filename = nets[n][0]

	if not os.path.exists(filename):
		url = "http://storage.sjeng.org/networks/{}".format(nets[n][0])
		f = requests.get(url)
		with open(filename, "wb") as output:
			output.write(f.content)
