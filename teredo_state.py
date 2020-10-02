# netsh interface teredo set state disabled
# netsh interface teredo set state type=enterpriseclient

import subprocess, time

foo = subprocess.check_output("netsh interface teredo show state")

print(foo.decode())		# From its bytes

input()
