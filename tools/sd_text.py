"""sd_text.py ROM: Scrapyard Dog's text inventory.
 1. the message table f7:D94B (42 words) and each message decoded (control bytes shown);
 2. the shop lines b5:B149 (48 words -> distinct 26-byte lines);
 3. runs in the 'letter' font (codes $5C-$7E, $5F = space), any bank;
 4. totals."""
import sys

rom = open(sys.argv[1], "rb").read()[128:]


def off(bank, a):
    if a >= 0xC000:
        return 7 * 0x4000 + a - 0xC000
    if a < 0x8000:
        return 6 * 0x4000 + a - 0x4000
    return bank * 0x4000 + a - 0x8000


def w(bank, a):
    o = off(bank, a)
    return rom[o] | (rom[o + 1] << 8)


def show(b):
    if 0x20 <= b < 0x60:
        return chr(b)
    return "<%02X>" % b


def main():
    print("== messages, f7:D94B ==")
    ptrs = [w(7, 0xD94B + 2 * i) for i in range(42)]
    total = 0
    chars = 0
    for i, p in enumerate(ptrs):
        o = off(7, p)
        style = rom[o]
        j = o + 1
        while rom[j] != 0:
            j += 1
        body = rom[o + 1:j]
        n = j + 1 - o
        total += n
        chars += sum(1 for b in body if 0x20 <= b < 0x60)
        print("%02X %04X style %d len %3d  %s" % (i, p, style, n, "".join(show(b) for b in body)))
    print("message bytes %d (+ %d table) ; printable characters %d" % (total, 84, chars))
    print("== shop lines, b5:B149 ==")
    sp = [w(5, 0xB149 + 2 * i) for i in range(48)]
    d = sorted(set(sp))
    for p in d:
        o = off(5, p)
        print("%04X %s  used %d" % (p, "".join(show(b) for b in rom[o:o + 26]), sp.count(p)))
    print("distinct lines %d x 26 = %d bytes, table 96; 48 lines unshared would be %d" % (len(d), len(d) * 26, 48 * 26))
    print("== letter-font runs (>= 12 bytes of $5C-$7E) ==")
    i = 0
    while i < len(rom):
        j = i
        while j < len(rom) and 0x5C <= rom[j] <= 0x7E:
            j += 1
        if j - i >= 12 and rom[i:j].count(0x5F) >= 2 and len(set(rom[i:j])) > 5:
            b, r = i // 0x4000, i % 0x4000
            a = (0xC000 if b == 7 else 0x4000 if b == 6 else 0x8000) + r
            t = "".join(" " if c == 0x5F else "." if c == 0x7E else "'" if c == 0x5E else "-" if c == 0x5C else chr(c) for c in rom[i:j])
            print("%d:%04X len %d  %s" % (b, a, j - i, t))
        i = j + 1


if __name__ == "__main__":
    main()
