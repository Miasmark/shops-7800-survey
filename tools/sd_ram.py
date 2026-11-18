"""sd_ram.py DUMP ADDR [LEN]   hex + ASCII of a 64K dump (run.lua's dump_fNNNNN.bin)."""
import sys
d = open(sys.argv[1], "rb").read()
a = int(sys.argv[2], 16)
n = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x40
for i in range(a, a + n, 16):
    row = d[i:i + 16]
    print("%04X  %-48s %s" % (i, " ".join("%02X" % b for b in row), "".join(chr(b) if 32 <= b < 127 else "." for b in row)))
