"""sd_find.py ROM text|hex:AABB..  find a byte string in every bank; prints bank:addr (window addr).
   sd_find.py ROM --strings MIN   list ASCII runs (20-5F range allowed + control bytes shown as <xx>) >= MIN."""
import sys

def addr(o):
    b = o // 0x4000
    r = o % 0x4000
    if b == 7:
        return "7:%04X" % (0xC000 + r)
    if b == 6:
        return "6:%04X" % (0x4000 + r)
    return "%d:%04X" % (b, 0x8000 + r)

def main():
    rom = open(sys.argv[1], "rb").read()[128:]
    if sys.argv[2] == "--strings":
        mn = int(sys.argv[3])
        i = 0
        while i < len(rom):
            j = i
            while j < len(rom) and 0x20 <= rom[j] <= 0x5F:
                j += 1
            if j - i >= mn and len(set(rom[i:j])) > 4:
                print(addr(i), repr(rom[i:j].decode("ascii")), "next=%02X %02X %02X" % tuple(rom[j:j + 3]))
            i = j + 1
        return
    pat = sys.argv[2]
    if pat.startswith("hex:"):
        p = bytes.fromhex(pat[4:])
    else:
        p = pat.encode("ascii")
    i = rom.find(p)
    while i >= 0:
        print(addr(i))
        i = rom.find(p, i + 1)

if __name__ == "__main__":
    main()
