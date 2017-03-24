import os, re
import gofish

IN_DIR = "61on"
OUT_DIR = "bar"

def list_map(arr, func):
	return list(map(func, arr))

def list_filter(arr, func):
	return list(filter(func, arr))

all_things = list_map(os.listdir(IN_DIR), lambda x : os.path.join(IN_DIR, x))
all_files = list_filter(all_things, lambda x : os.path.isfile(x))

for filename in all_files:

    root = gofish.load(filename)

    root.safe_commit("CA", "utf-8")
    root.safe_commit("KM", 6.5)

    for key in ["GN", "HA", "TT", "TM", "TC", "AP"]:
        root.safe_commit(key, "")

    for key in ["PW", "PB"]:
    	if root.properties[key] == ["绝艺"]:
    		root.properties[key] = ["绝艺 (Fine Art)"]

    black, white, date, gid = re.search(r"\[(.+)\]vs\[(.+)\](\d\d\d\d\d\d\d\d)(\d\d\d\d\d\d\d\d).sgf", filename).group(1, 2, 3, 4)
    newfilename = os.path.join(OUT_DIR, "{} {} vs {} ({}).sgf".format(date, black, white, gid))

    gofish.save_file(newfilename, root)
