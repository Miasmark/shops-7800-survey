"""sd_refs.py ROM LO HI [w]   every 3-byte instruction whose absolute operand is in LO..HI (hex).
With 'w', only writers (STA/STX/STY/INC/DEC/ASL/LSR/ROL/ROR abs and indexed). A byte scan, not a
trace: hits in data are possible (check the listing)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                                "a7800-toolkit", "tools"))
import m6502  # noqa: E402

W = {"STA", "STX", "STY", "INC", "DEC", "ASL", "LSR", "ROL", "ROR"}


def addr(o):
    b, r = o // 0x4000, o % 0x4000
    if b == 7:
        return "7:%04X" % (0xC000 + r)
    if b == 6:
        return "6:%04X" % (0x4000 + r)
    return "%d:%04X" % (b, 0x8000 + r)


def main():
    rom = open(sys.argv[1], "rb").read()[128:]
    lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
    wonly = len(sys.argv) > 4
    for o in range(len(rom) - 2):
        op = rom[o]
        mn, md, il = m6502.OPCODES[op]
        if il == "*" or md not in ("abs", "abx", "aby"):
            continue
        v = rom[o + 1] | (rom[o + 2] << 8)
        if lo <= v <= hi and (not wonly or mn in W):
            print("%s  %s $%04X%s" % (addr(o), mn, v, {"abs": "", "abx": ",X", "aby": ",Y"}[md]))


if __name__ == "__main__":
    main()
