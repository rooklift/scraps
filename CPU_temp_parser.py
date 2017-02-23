LOGFILENAME = "Real Temp/RealTempLog.txt"

maxtemp = 0
maxload = 0

logfile = open(LOGFILENAME)

for line in logfile:
	try:
		parts = line.split()
		coretemps = parts[3:7]
		for temp in coretemps:
			if int(temp) > maxtemp:
				maxtemp = int(temp)
		load = parts[7]
		if float(load) > maxload:
			maxload = float(load)
	except:
		pass

print("Max temperature seen in log file:")
print("   " + str(maxtemp) + " C")
print()
print("Max load seen in log file:")
print("   " + str(maxload) + " %")

input()
