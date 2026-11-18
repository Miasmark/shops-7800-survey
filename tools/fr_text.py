"""fr_text.py ROM: list Fatal Run's text runs in both encodings.
 A: plain ASCII (letters, digits, space, a little punctuation), runs of 4+ with at least 3 letters.
 T: tile codes (the 4-pixel font's column numbers): $50-$69 = A-Z, digits $00,$08,..,$48, $7B blank,
    runs of 4+ with at least 3 letters. python -I."""
import sys

def tile(b):
    if 0x50 <= b <= 0x69:
        return chr(b - 0x0F)
    if b == 0x7B:
        return " "
    if b % 8 == 0 and b <= 0x48:
        return chr(0x30 + b // 8)
    return None

def asc(b):
    c = chr(b)
    if c.isupper() or c.isdigit() or c in " -.,'!?$/:":
        return c
    return None

def runs(rom, fn, tag):
    out = []
    i = 0
    n = len(rom)
    while i < n:
        j = i
        s = ""
        while j < n and fn(rom[j]) is not None and (j // 0x4000) == (i // 0x4000):
            s += fn(rom[j])
            j += 1
        letters = sum(1 for c in s if c.isupper())
        if len(s) >= 4 and letters >= 3 and len(set(s)) > 2:
            b = i // 0x4000
            a = (i % 0x4000) + (0xC000 if b == 7 else 0x8000)
            out.append((b, a, tag, s))
        i = max(j, i + 1)
    return out

def main():
    rom = open(sys.argv[1], "rb").read()[128:]
    res = runs(rom, asc, "A") + runs(rom, tile, "T")
    res.sort()
    tot = {"A": 0, "T": 0}
    for b, a, tag, s in res:
        tot[tag] += len(s)
        print("%d:%04X %s %3d '%s'" % (b, a, tag, len(s), s))
    print("total bytes: ASCII %d, tile-coded %d" % (tot["A"], tot["T"]))

if __name__ == "__main__":
    main()
