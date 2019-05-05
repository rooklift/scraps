import os.path
import struct
import sys

class WAV (object):				# Makes many assumptions about format, e.g. bitrate, 2 channels, etc

	def __init__(self):
		four_null_bytes = b'\0\0\0\0'
#													-- Name --							-- Pos --
		self.headers = bytearray(
			b'RIFF' +								# ChunkID							#  0
			four_null_bytes +						# ChunkSize (set later)				#  4
			b'WAVE' +								# Format							#  8
			b'fmt ' +								# Subchunk1ID						# 12
			struct.pack('<I', 16) +					# Subchunk1Size						# 16
			struct.pack('<H', 1) +					# AudioFormat						# 20
			struct.pack('<H', 2) +					# NumChannels						# 22
			struct.pack('<I', 44100) +				# SampleRate						# 24
			struct.pack('<I', 176400) +				# ByteRate							# 28
			struct.pack('<H', 4) +					# BlockAlign						# 32
			struct.pack('<H', 16) +					# BitsPerSample						# 34
			b'data' +								# Subchunk2ID						# 36
			four_null_bytes							# Subchunk2Size (set later)			# 40
		)
		self.data = bytearray()															# 44

	def fix_headers(self):
		self.headers[4:8] = struct.pack('<I', 36 + len(self.data))
		self.headers[40:44] = struct.pack('<I', len(self.data))

	def write(self, filename):
		self.fix_headers()
		outfile = open(filename, "wb")
		outfile.write(self.headers)
		outfile.write(self.data)
		outfile.close()

if len(sys.argv) == 1:
	print("Usage: {} <filenames>".format(os.path.basename(sys.argv[0])))
	input()
	exit()
else:
	for name in sys.argv[1:]:
		print(name)
		infile = open(name, "rb")
		wav = WAV()

		infile.read(512)		# Skip the headers (not sure if they are always same size though)

		while 1:
			newdata = infile.read(1024)
			if len(newdata):
				wav.data += newdata
			else:
				break

		infile.close()

		outfilename = name + ".wav"
		wav.write(outfilename)
