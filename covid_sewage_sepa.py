import datetime, re, sys
import matplotlib.pyplot as plt

# For reading csv from https://informatics.sepa.org.uk/RNAmonitoring/

class DataPoint:
	def __init__(self, date, value):
		self.date = datetime.datetime.strptime(date, "%d/%m/%Y")
		self.value = int(float(value))

def load_sites(lines):		# Area   Site   Date   Pop-band   Population   Result Description   Reported Value   Days Since
	sites = dict()
	for line in lines:
		tokens = line.split("\t")
		site = tokens[1]
		if site in sites:
			sitedata = sites[site]
		else:
			sitedata = []
			sites[site] = sitedata
		sitedata.append(DataPoint(date = tokens[2], value = tokens[6]))
	return sites

def draw(sites):
	for site in sites:
		sitedata = sites[site]
		x = [o.date for o in sitedata]
		y = [o.value for o in sitedata]
		plt.plot(x, y)
	plt.show()

def main():
	with open(sys.argv[1], "rb") as f:
		raw = f.read()
		decoded = raw.decode("utf-16-le")
		lines = [s.strip() for s in decoded.split("\n") if s.strip() != ""]
	sites = load_sites(lines[1:])		# Skip top line, which is headings
	draw(sites)

main()
