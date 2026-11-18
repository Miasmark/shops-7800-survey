"""sd_pad.py ROM: how much of Scrapyard Dog's text is padding (spaces used to centre or fill rows)."""
import sys
rom = open(sys.argv[1], "rb").read()[128:]
def o7(a): return 7 * 0x4000 + a - 0xC000
def o5(a): return 5 * 0x4000 + a - 0x8000
def o4(a): return 4 * 0x4000 + a - 0x8000
lead = 0
for i in range(42):
    p = rom[o7(0xD94B + 2 * i)] | (rom[o7(0xD94C + 2 * i)] << 8)
    o = o7(p) + 1
    line = True
    while rom[o] != 0:
        b = rom[o]
        if b == 0x0D:
            line = True
        elif b == 0x20 and line:
            lead += 1
        else:
            line = False
        o += 1
print("messages: leading spaces (centring)", lead, "of 1548")
ptrs = sorted({rom[o5(0xB149 + 2 * i)] | (rom[o5(0xB14A + 2 * i)] << 8) for i in range(48)})
pad = 0
for p in ptrs:
    row = rom[o5(p):o5(p) + 26]
    s = bytes(row).decode("latin1")
    pad += 26 - len(s.strip(" "))
print("shop lines: leading+trailing spaces", pad, "of", 26 * len(ptrs))
row = rom[o4(0x9604):o4(0x9604) + 144]
pad = 0
for r in range(6):
    s = bytes(row[r * 24:r * 24 + 24]).decode("latin1")
    pad += 24 - len(s.strip("_"))
print("letter: leading+trailing blanks", pad, "of 144")
