"""sd_dis.py ROM BANK START [LEN]   linear 6502 disassembly at a CPU address (hex), for reading
untraced code. BANK is the window bank (ignored for 4000-7FFF = bank 6 and C000+ = bank 7)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                                "a7800-toolkit", "tools"))
import m6502  # noqa: E402

REG = {0x20: "BACKGRND", 0x2C: "DPPH", 0x30: "DPPL", 0x34: "CHARBASE", 0x3C: "CTRL", 0x28: "MSTAT",
       0x24: "WSYNC", 0x38: "OFFSET", 0x280: "SWCHA", 0x282: "SWCHB", 0x0C: "INPT4", 0x0D: "INPT5",
       0x08: "INPT0", 0x09: "INPT1", 0x01: "INPTCTRL"}


def off(bank, a):
    if a >= 0xC000:
        return 7 * 0x4000 + a - 0xC000
    if a < 0x8000:
        return 6 * 0x4000 + a - 0x4000
    return bank * 0x4000 + a - 0x8000


def main():
    rom = open(sys.argv[1], "rb").read()[128:]
    bank = int(sys.argv[2])
    pc = int(sys.argv[3], 16)
    ln = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0x60
    end = pc + ln
    while pc < end:
        o = off(bank, pc)
        op = rom[o]
        mn, md, il = m6502.OPCODES[op]
        n = m6502.MODES[md]
        b = rom[o:o + 1 + n]
        if n == 1:
            v = b[1]
            if md == "rel":
                t = pc + 2 + (v - 256 if v > 127 else v)
                s = "$%04X" % t
            elif md == "imm":
                s = "$%02X" % v
            else:
                s = REG.get(v, "$%02X" % v)
        elif n == 2:
            v = b[1] | (b[2] << 8)
            s = REG.get(v, "$%04X" % v)
        else:
            s = ""
        print("%04X: %-9s %s %s%s" % (pc, " ".join("%02X" % x for x in b), mn, m6502.FMT[md].format(v=s),
                                       "   ; illegal" if il == "*" else ""))
        pc += 1 + n
        if mn in ("RTS", "JMP", "RTI"):
            print()


if __name__ == "__main__":
    main()
