import os, re
import gofish

IN_DIR = "foo"
OUT_DIR = "bar"

all_things = list(map(lambda x : os.path.join(IN_DIR, x), os.listdir(IN_DIR)))
all_files = list(filter(lambda x : os.path.isfile(x), all_things))

for filename in all_files:

    root = gofish.load(filename)
    
    root.safe_commit("CA", "utf-8")
    root.safe_commit("KM", 6.5)
    
    for key in ["GN", "HA", "TT", "TM", "TC", "AP"]:
        root.safe_commit(key, "")

    black, white, date, gid = re.search(r"\[(.+)\]vs\[(.+)\](\d\d\d\d\d\d\d\d)(\d\d\d\d\d\d\d\d).sgf", filename).group(1, 2, 3, 4)
    newfilename = os.path.join(OUT_DIR, "{} {} vs {} ({}).sgf".format(date, black, white, gid))

    gofish.save_file(newfilename, root)
