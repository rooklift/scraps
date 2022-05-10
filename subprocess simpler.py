import subprocess

p = subprocess.Popen("C:\\Programs (self-installed)\\Chess Engines\\stockfish_15_x64_avx2.exe",
    stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.DEVNULL)

p.stdin.write("uci\n".encode("utf8"))
p.stdin.flush()

while True:
    print(p.stdout.readline().decode("utf8"), end = "")
