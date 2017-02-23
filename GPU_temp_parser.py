LOGFILENAME = "GPU-Z Sensor Log.txt"

maxtemp = 0
maxspeed = 0
maxload = 0

logfile = open(LOGFILENAME)

for n, line in enumerate(logfile):
	parts = line.split(",")
	temp = parts[3].strip()
	speed = parts[4].strip()
	load = parts[6].strip()
	
	try:
		if float(temp) > maxtemp:
			maxtemp = float(temp)
		if int(speed) > maxspeed:
			maxspeed = int(speed)
		if int(load) > maxload:
			maxload = int(load)
	except:
		pass

print("Max temperature seen in log file:")
print("   " + str(maxtemp) + " C")
print()
print("Max fan speed seen in log file:")
print("   " + str(maxspeed) + " %")
print()
print("Max load seen in log file:")
print("   " + str(maxload) + " %")

input()
