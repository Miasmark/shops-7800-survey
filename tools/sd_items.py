"""sd_items.py: enter the shop with each item (0-7) in world W (default 0), buy once with 50 coins,
snapshot, and print the counter changes. Entry is FORCED: one JSR in the level loop (f6:4390) is
diverted for a frame to the door routine f6:48C8 with door index 6 (the level bank's own record
'00 FF 3F 00 00 01' = shop, item 0), and the item byte written to $25B1 is substituted by a write
tap; world by a poke of $2227 at the same frame. Runs in scrapyard/runs/item<W>_<n>."""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PEEK = "22A5,22B3,22A7,22A9,22AB,22AD,22BB,22AF,22B1,2497,25B1,221B"


def run(w, item, money="50", tag=""):
    name = "item%d_%d%s" % (w, item, tag)
    script = "200:-:0;10:-:1;200:-:0;10:-:1;200:-:0;10:-:1;260:-:0;10:r:0;20:-:0;6:-:3;120:-:0;10:l:0;20:-:0;6:-:3;200:-:0"
    cmd = [sys.executable, os.path.join(HERE, "sd_run.py"), "scrapyard", name, "lua=sd_patch.lua",
           "sd_tools=" + HERE.replace("\\", "/"), "script=" + script,
           "patch=800-801:4391=C8,4392=48", "subst=800-802:25B1:01=%02X" % (item * 16 + 1),
           "pokes=799:EC=04,ED=E0,EF=06,2227=%02X;830:22A5=%s,22B3=00" % (w, money),
           "snaps=880,1000", "end=1200", "dumps=880", "peek=" + PEEK]
    subprocess.run(cmd, stdout=subprocess.DEVNULL)
    rd = os.path.join(ROOT, "scrapyard", "runs", name)
    lines = open(os.path.join(rd, "frames.txt")).read().split("\n")
    keep = [l for l in lines if l and 825 <= int(l.split()[0]) <= 1200]
    return name, keep


def main():
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    money = sys.argv[2] if len(sys.argv) > 2 else "50"
    tag = sys.argv[3] if len(sys.argv) > 3 else ""
    items = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else list(range(8))
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda i: run(w, i, money, tag), items))
    print("frame " + PEEK)
    for name, keep in res:
        print(name)
        last = None
        for l in keep:
            v = l.split()[1:]
            key = v[:9] + v[10:]
            if key != last:
                print("   " + l)
                last = key


if __name__ == "__main__":
    main()
