"""fr_inventory.py ROM: Fatal Run's text, decoded and counted. python -I.
Writes the list to stdout (kept in fatalrun/text_inventory.txt)."""
import sys

rom = open(sys.argv[1], "rb").read()[128:]

def off(bank, a):
    if a >= 0xC000:
        return 7 * 0x4000 + a - 0xC000
    if a < 0x8000:
        return 6 * 0x4000 + a - 0x4000
    return bank * 0x4000 + a - 0x8000

def b(bank, a, n=1):
    o = off(bank, a)
    return rom[o:o + n]

def w(bank, a):
    x = b(bank, a, 2)
    return x[0] | x[1] << 8

def tile(v):
    if 0x50 <= v <= 0x69:
        return chr(v - 0x0F)
    if v == 0x7B:
        return " "
    if v % 8 == 0 and v <= 0x48:
        return chr(0x30 + v // 8)
    return "<%02X>" % v

total = {}
def add(k, n):
    total[k] = total.get(k, 0) + n

# --- bank 4: the ticker's word list and messages ---
print("== HUD ticker (bank 4) ==")
words = {}
a = 0xAAE1
while a < 0xABDF:
    s = b""
    st = a
    while b(4, a)[0]:
        s += b(4, a)
        a += 1
    a += 1
    words[st - 0xAAE0] = s.decode()
print("word list 4:AAE0-4:ABDE, %d words, %d bytes with terminators" % (len(words), 0xABDF - 0xAAE0))
add("ticker word list", 0xABDF - 0xAAE0)
a = 0xAA32
msgs = []
while a < 0xAAE0:
    st = a
    t = []
    while b(4, a)[0]:
        t.append(b(4, a)[0])
        a += 1
    a += 1
    msgs.append((st, t))
plain = 0
for st, t in msgs:
    txt = " ".join(words.get(x, "?%02X" % x) for x in t)
    plain += len(txt) + 1 if t else 0
    print("  4:%04X (index %02X) %-12s %s" % (st, st - 0xAA31, " ".join("%02X" % x for x in t), txt))
print("messages: %d records, %d token bytes with terminators; the same messages spelled out would be %d bytes"
      % (len(msgs), 0xAAE0 - 0xAA32, plain))
add("ticker message tokens", 0xAAE0 - 0xAA32)
cred = b(4, 0xABDF, 0xAC9F - 0xABDF)
story = b(4, 0xAC9F, 0xAD9C - 0xAC9F)
print("credits ticker 4:ABDF %d bytes: %s" % (len(cred), cred.rstrip(b"\0").decode()))
print("story ticker   4:AC9F %d bytes: %s" % (len(story), story.rstrip(b"\0").decode()))
add("credits ticker", len(cred))
add("story ticker", len(story))
add("ticker ASCII-to-tile table 4:AD9C", 0x3B)

# --- bank 0: the shop ---
print("== shop (bank 0) ==")
names = [w(0, 0x98B4 + 2 * i) for i in range(19)]
prices = [w(0, 0x9C0D + 2 * i) for i in range(19)]
repair = [w(0, 0x9E39 + 2 * i) for i in range(19)]
subs = [w(0, 0x9AAD + 2 * i) for i in range(19)]
seen = set()
for i in range(19):
    nm = b(0, names[i], 10).decode()
    st = []
    for k in range(4):
        p = w(0, subs[i] + 2 * k)
        st.append("%04X:%s" % (p, b(0, p, 10).decode().strip() or "-"))
        seen.add(p)
    print("  item %02X name 0:%04X '%s' price $%04X repair $%04X types %s" % (i, names[i], nm, prices[i], repair[i], " ".join(st)))
seen.discard(0x94A4)
dn = len(set(names) - {0x94A4})
print("distinct names %d x 10 = %d bytes; distinct type names %d x 10 = %d bytes" % (dn, dn * 10, len(seen - set(names)), len(seen - set(names)) * 10))
add("shop item names (10-byte fields)", dn * 10)
add("shop type names (10-byte fields)", len(seen - set(names)) * 10)
add("shop pointers (names 38, type lists 38, type words)", 38 + 38 + 2 * 4 * len(set(subs)))
add("shop headings COST/AMOUNT/STATUS/blank/BONUS/digits", 32 + 5 + 12)
add("shop ASCII-to-tile table 0:9878", 0x3C)
pad = 0
for p in (set(names) | seen) - {0x94A4}:
    s = b(0, p, 10).decode()
    pad += 10 - len(s.strip())
print("padding spaces inside the 10-byte fields: %d" % pad)

# --- others ---
print("== other ==")
print("bonus screen labels 6:559A (tile codes): ".join(tile(x) for x in b(6, 0x559A, 18)))
add("bonus screen labels", 18)
pw = b(4, 0xBF01, 120)
print("password words 4:BF01 (tile codes, 8 a word): " + " | ".join("".join(tile(x) for x in pw[i:i + 8]) for i in range(0, 120, 8)))
add("password words + PASSWORD", 120)
print("title menu 4:BBB8: " + b(4, 0xBBB8, 16).decode())
add("title menu", 16)
print("game over 4:9E4A (tile codes): ".join(tile(x) for x in b(4, 0x9E4A, 10)))
add("game over", 9)
print("high scores 4:9FAC (tile codes): ".join(tile(x) for x in b(4, 0x9FAC, 42)))
add("high score headings", 42)
print("== totals ==")
t = 0
for k, v in total.items():
    print("  %-52s %5d" % (k, v))
    t += v
print("  %-52s %5d" % ("all text, tables included", t))
