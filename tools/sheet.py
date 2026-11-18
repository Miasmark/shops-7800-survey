"""sheet.py OUT.png COLS file.png ...   tile screenshots into one labelled sheet (Pillow)."""
import os
import sys
from PIL import Image, ImageDraw

def main():
    out, cols = sys.argv[1], int(sys.argv[2])
    files = sys.argv[3:]
    ims = [Image.open(f).convert("RGB") for f in files]
    w, h = ims[0].size
    sc = 1
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new("RGB", (cols * w * sc, rows * (h * sc + 12)), (40, 40, 40))
    d = ImageDraw.Draw(sh)
    for i, im in enumerate(ims):
        x, y = (i % cols) * w * sc, (i // cols) * (h * sc + 12)
        sh.paste(im, (x, y + 12))
        d.text((x + 2, y), os.path.basename(files[i])[-16:-4], fill=(255, 255, 0))
    sh.save(out)

if __name__ == "__main__":
    main()
