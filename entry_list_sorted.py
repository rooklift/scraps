import requests


class Player:

	def __init__(self, name, rank, club, country):
		try:
			self.forename = name.split(",")[1].strip()
			self.surname = name.split(",")[0].strip()
		except:
			self.forename = name
			self.surname = name
		self.rank = rank
		self.club = club
		self.country = country

	def is_kyu(self):
		return self.rank.endswith("k")

	def is_dan(self):
		return self.rank.endswith("d")

	def is_rankless(self):
		return not self.is_kyu() and not self.is_dan()

	def fullname(self):
		return self.forename + " " + self.surname

	def dist_to_10d(self):
		if self.is_rankless():
			return 100
		else:
			numpart = int(self.rank[:-1])
			if self.is_dan():
				return 10 - numpart
			else:
				return 9 + numpart

	def __str__(self):
		return "\t{0: >4}  {1: <26} {2}".format(self.rank, self.fullname(), self.club)

	def __lt__(self, other):
		return self.dist_to_10d() < other.dist_to_10d()


def main(url):

	html = requests.get(url).text

	i1 = html.find("</thead>") + len("</thead>")
	i2 = html.find("</table>")

	table = html[i1:i2].strip()

	table = table.replace("<td class=\"te_right\">", "<td>")
	table = table.replace("<tr><td>", "")
	table = table.replace("</td></tr>", "")

	names = set()		# For deduplication
	players = []
	dupes = []

	for line in table.split("\n"):
		num, name, rank, club, country = line.split("</td><td>")
		if num.isnumeric():
			if name not in names:
				players.append(Player(name, rank, club, country))
				names.add(name)
			else:
				dupes.append(name)

	players.sort()

	print()
	for p in players:
		print(p)

	print()
	print("Dupes:", dupes)


if __name__ == "__main__":
	url = input("URL? ")
	main(url)
	input()

