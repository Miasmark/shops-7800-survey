"""sd_run.py (run.py with lua=FILE in tools/ to pick the autoboot script) GAME NAME key=value ...   one windowless MAME session (the fork), in GAME/runs/NAME.
GAME is fatalrun or scrapyard (roms/GAME.a78). Keys are run.lua's environment variables in lower
case: script, snaps, end, pokes, hold, peek, dumps, wtap, wfrom, wto, wmax, rtap, rfrom, rto,
exec, xfrom, xto.  Screenshots are renamed NAME_fNNNNN.png. Never opens a window."""
import glob
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAME = os.environ.get("A7800_MAME", "a78.exe")


def main():
    game, name = sys.argv[1:3]
    kv = dict(a.split("=", 1) for a in sys.argv[3:])
    rd = os.path.join(ROOT, game, "runs", name)
    shutil.rmtree(rd, ignore_errors=True)
    os.makedirs(os.path.join(rd, "cfg"))
    open(os.path.join(rd, "ui.ini"), "w").write("skip_warnings 1\n")
    shutil.copy(os.path.join(ROOT, "roms", game + ".a78"), os.path.join(rd, "cart.a78"))
    env = dict(os.environ)
    for k, v in kv.items():
        env[k.upper()] = v
    cmd = [MAME, "a7800", "-cart", "cart.a78", "-bios", "skip", "-skip_gameinfo", "-video", "none",
           "-sound", "none", "-nothrottle", "-inipath", ".", "-cfg_directory", "cfg",
           "-nvram_directory", "nv", "-snapshot_directory", "snap",
           "-autoboot_script", os.path.join(HERE, kv.pop("lua", "run.lua"))]
    with open(os.path.join(rd, "mame.out"), "w") as o:
        subprocess.run(cmd, cwd=rd, env=env, stdout=o, stderr=subprocess.STDOUT, timeout=3000)
    snaps = sorted(int(x) for x in kv.get("snaps", "").split(",") if x)
    files = sorted(glob.glob(os.path.join(rd, "snap", "a7800", "*.png")))
    for fpath, fr in zip(files, snaps):
        os.replace(fpath, os.path.join(rd, "%s_f%05d.png" % (name, fr)))
    out = open(os.path.join(rd, "mame.out")).read().strip()
    print("%s/%s: %d/%d snaps%s" % (game, name, len(files), len(snaps), ("\n" + out[-600:]) if out else ""))


if __name__ == "__main__":
    main()
