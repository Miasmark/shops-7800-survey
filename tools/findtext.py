"""findtext.py ROM WORD [WORD...]: search a cart for a word under every constant byte offset
(letter + k), and with bit 7 or 6 varying ignored. Prints bank:address and the offset. python -I."""
import sys

def main():
    rom = open(sys.argv[1], "rb").read()[128:]
    for w in sys.argv[2:]:
        wb = w.encode()
        for k in range(256):
            pat = bytes((c + k) & 0xFF for c in wb)
            i = rom.find(pat)
            while i >= 0:
                b = i // 0x4000
                a = (i % 0x4000) + (0xC000 if b == 7 else 0x8000)
                print("%-10s offset +%02X at %d:%04X%s" % (w, k, b, a, " (also 6:%04X)" % (a - 0x4000) if b == 6 else ""))
                i = rom.find(pat, i + 1)
        # differences only (any substitution cipher that keeps alphabet order)
if __name__ == "__main__":
    main()
