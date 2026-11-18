"""hx.py ROM BANK START [LEN] [--xor N] [--sub N]: hex + ASCII dump of a cart address.
BANK is 0-7; START is a CPU address (4000-7FFF = bank 6, C000-FFFF = bank 7, else BANK at 8000).
Run with python -I."""
import sys

def load(p):
    d = open(p, "rb").read()
    return d[128:]

def off(bank, addr):
    if addr >= 0xC000:
        return 7 * 0x4000 + addr - 0xC000
    if addr < 0x8000:
        return 6 * 0x4000 + addr - 0x4000
    return bank * 0x4000 + addr - 0x8000

def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    rom = load(a[0])
    bank = int(a[1])
    start = int(a[2], 16)
    ln = int(a[3], 16) if len(a) > 3 else 0x100
    sub = 0
    for x in sys.argv[1:]:
        if x.startswith("--sub="):
            sub = int(x[6:], 16)
    o = off(bank, start)
    for i in range(0, ln, 16):
        row = rom[o + i:o + i + 16]
        txt = "".join(chr((b - sub) & 0x7F) if 32 <= ((b - sub) & 0x7F) < 127 else "." for b in row)
        print("%d:%04X  %-48s %s" % (bank, start + i, " ".join("%02X" % b for b in row), txt))

if __name__ == "__main__":
    main()
