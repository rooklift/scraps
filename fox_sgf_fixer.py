import os, re
import gofish

IN_DIR = "foo"
OUT_DIR = "bar"

KNOWN_PLAYERS = {
	"绝艺":			"Fine Art",
	"星宿老仙":		"Gu Li",
	"潜伏":			"Ke Jie",
	"剑过无声":		"Lian Xiao",
	"airforce9":	"Kim Jiseok",
	"Eason":		"Zhou Ruiyang",
	"INDIANA13":	"Gu Zihao",
	"jpgo01":		"Iyama Yuta",
	"leaf":			"Shi Yue",
	"maker":		"Park Junghwan",
	"Master":		"AlphaGo",
	"nparadigm":	"Shin Jinseo",
}

def list_map(arr, func):
	return list(map(func, arr))

def list_filter(arr, func):
	return list(filter(func, arr))

all_things = list_map(os.listdir(IN_DIR), lambda x : os.path.join(IN_DIR, x))
all_files = list_filter(all_things, lambda x : os.path.isfile(x))

for filename in all_files:

    root = gofish.load(filename)

    root.safe_commit("CA", "utf-8")
    root.safe_commit("KM", 6.5)			# FIXME

    for key in ["GN", "TT", "TM", "TC", "AP"]:
        root.delete_property(key)

    if "HA" in root.properties:
    	if root.properties["HA"] == ["0"]:
    		root.delete_property("HA")

    for key in ["PW", "PB"]:
    	orig = root.properties[key][0]
    	if orig in KNOWN_PLAYERS:
    		root.properties[key][0] = "{} ({})".format(orig, KNOWN_PLAYERS[orig])

    black, white, date, gid = re.search(r"\[(.+)\]vs\[(.+)\](\d\d\d\d\d\d\d\d)(\d\d\d\d\d\d\d\d).sgf", filename).group(1, 2, 3, 4)
    newfilename = os.path.join(OUT_DIR, "{} {} vs {} ({}).sgf".format(date, black, white, gid))

    gofish.save_file(newfilename, root)
