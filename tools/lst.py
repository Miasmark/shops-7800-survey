"""lst.py FILE.asm FROM TO: print a listing range compactly (address: instruction), labels kept.
FROM/TO are hex addresses as in the '; XXXX:' comments."""
import re
import sys

def main():
    f, a, b = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
    on = False
    pend = []
    for line in open(f, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        m = re.search(r";\s*([0-9A-F]{4})[: ]", line)
        if m and not line.startswith(";"):
            ad = int(m.group(1), 16)
            on = a <= ad <= b
            if on:
                for p in pend:
                    print(p)
                code = line.split(";")[0].strip()
                code = re.sub(r"\s+", " ", code)
                tail = ""
                mm = re.search(r"bank switch.*", line)
                if mm:
                    tail = "  ; " + mm.group(0)
                if code.startswith(".byte"):
                    print("%04X %s" % (ad, code))
                else:
                    print("%04X  %s%s" % (ad, code, tail))
            pend = []
        elif line and not line.startswith(";") and line.endswith(":"):
            pend.append(line)
        elif line.startswith("; xrefs") :
            pend.append(line[:100])

if __name__ == "__main__":
    main()
