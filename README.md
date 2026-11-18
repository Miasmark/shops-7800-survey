# Shops, menus and text in two Atari 7800 games: a survey

A survey of the between-stage shop, menu and text screens of *Fatal Run* (`Fatal Run (NTSC) (Atari) (1990) (A44DF354).a78`) and *Scrapyard Dog* (`Scrapyard Dog (NTSC) (Atari) (1990) (5CC8C34F).a78`), both 128K SuperGame.

## How this was made, and how far to trust it

This is the output of **one automated research pass** on 2026-11-18: a single AI agent
session (Claude, working through the a7800-toolkit and MAME) given a list of questions and
about half an hour, not a long-running hand disassembly like
[galaga-7800-disassembly](https://github.com/Miasmark/galaga-7800-disassembly) and its
siblings. A second session then checked the report's main tables and routines against the
ROM's bytes; they matched. Nothing here was checked on a console.

Treat a **live** tag as "one agent saw this in MAME once", a **code** tag as a reading, and
the coverage figures below as what the tracer reached, not what was understood.

## Effort: two games, one narrow subject

One agent, about 36 minutes, 89 tool calls, on seven questions: text storage, shops as
data, how the screen is drawn, item effects, screen flow and banking, passwords. The first
two were answered for both games with live confirmation; the rest mostly live, partly from
code.

| Game | Tracer coverage | Notes |
|---|---|---|
| Fatal Run | banks 6 and 7 45.5%, bank 4 31.5%, bank 0 25.8% (the shop's code fully traced), bank 3 12.3%, bank 2 7.7%, bank 5 1.8%, bank 1 untraced | the shop was reached by forcing the stage's end with the game's own test; password entry, the ending and the cheat bits' effects not determined |
| Scrapyard Dog | bank 6 59.7%, bank 7 19.5%, bank 5 6.2%, bank 4 5.2%, banks 0-3 untraced | shop entry was forced (one `JSR` operand read as the door routine for a frame); where shop doors are in the levels was not found |

Both listings round-trip. The findings say plainly which states were forced by pokes.

## What is here, and what is not

- `annotations.json`: entry points, labels, RAM names, data blocks and comments, in the
  [a7800-toolkit](https://github.com/Miasmark/a7800-toolkit)'s format.
- `docs/FINDINGS.md`: what the code does, with addresses, record formats and an evidence
  tag on every claim: **live** (watched in MAME: a tap, a trace, a RAM model, a poke that
  changed behaviour), **code** (read from the listing only), **hint** (a guess). Dead ends
  and corrections are kept in it.
- `tools/`: the probes and scripts the findings were made with.

**No ROM is here, and no listing.** A listing is the game's machine code in readable form;
it is rebuilt from `annotations.json` and your own legally owned dump with the toolkit's
`disasm.py`, and checked byte for byte with its `verify.py`. Captures, memory dumps,
renders of the graphics and traces are left out for the same reason.

## Running the tools

The scripts look for three things in the environment:

| Variable | What | Default |
|---|---|---|
| `A7800_ROMS` | the folder with your ROM dumps, named as below | `roms` |
| `A7800_TOOLKIT` | the a7800-toolkit's `tools` folder | `a7800-toolkit/tools` |
| `A7800_MAME` | a MAME with the Atari 7800 driver | `a78.exe` |

The live runs were made on [Miasmark/mame-Atari8bit7800](https://github.com/Miasmark/mame-Atari8bit7800),
windowless (`-video none -sound none -nothrottle`).

## Licence

MIT (see `LICENSE`) for the annotations, the findings and the tools. It does not cover the
games, which belong to their owners; nothing of theirs is distributed here.

## The session's own notes

Shop, menu and text screens of two retail Atari 7800 games, read for techniques a homebrew
could reuse: **Fatal Run** and **Scrapyard Dog** (both Atari, 1990, 128K SuperGame).
ROM copies in a local `roms/` folder are for local work only and are not in the repository.

## Layout

- `docs/` FINDINGS.md.
- `roms/` fatalrun.a78, scrapyard.a78 (copies from the ROM library).
- `fatalrun/`, `scrapyard/` per game:
  - `annotations.json` what was learned (labels, RAM names, data blocks, entries from traces);
  - `src/*.asm` the generated listing (round-trips; regenerate, don't edit);
  - `text_inventory.txt` every text found, decoded and counted;
  - `survey.txt`, execution traces (`xt_*.log`), `runs/<name>/` one folder per MAME run
    (screenshots, `frames.txt` RAM peeks, `wtap.txt`/`rtap.txt` taps, `exec.txt` coverage,
    `dump_fNNNNN.bin` 64K dumps with `maria_fNNNNN.txt` register writes);
  - `tools/annotate.py` writes the hand annotations into `annotations.json`.
- `tools/` shared scripts:
  - `run.py GAME NAME key=value...` one windowless MAME session (the fork, `-video none`,
    own cfg/nvram/snapshot folders, `ui.ini` with `skip_warnings 1`); `run.lua` is its probe
    (scripted inputs, pokes, peeks, dumps, write/read taps, execution coverage);
  - `hx.py` hex dump by bank:address, `lst.py` compact listing range, `sheet.py` contact sheet,
    `findtext.py` word search under any constant offset;
  - `fr_text.py`, `fr_inventory.py` Fatal Run's text; `sd_*.py`, `sd_*.lua` Scrapyard Dog's probes.

## Rebuilding a listing

    python -I ../../a7800-toolkit/tools/disasm.py roms/fatalrun.a78 -c fatalrun/annotations.json -o fatalrun/src
    python -I ../../a7800-toolkit/tools/verify.py roms/fatalrun.a78 -d fatalrun/src

## Reaching the shops

- Fatal Run: start a game, then poke `$22B9=07, $22AF=C0` (the stage-end test at `7:D353`); a
  button press skips the town screen; the shop is up about 400 frames later. Example:

      python tools/run.py fatalrun shop "script=200:-:0;10:-:1;60:-:0;10:-:1;60:-:0;10:-:1;300:-:0;10:-:1;400:-:0" pokes="340:22B9=07,22AF=C0" snaps=900 end=1000

  Poke `$49=03` first to get a fourth-stage shop (password line, the TV on the wall).
- Scrapyard Dog: the shop was entered by a forced call of the door routine (`tools/sd_patch.lua`);
  see FINDINGS.

## Coverage (stated as it is)

- Fatal Run: bank 6 45.5%, bank 7 45.5%, bank 4 31.5%, bank 0 25.8% (the shop's code is fully
  traced; the rest of the bank is data and graphics), bank 3 12.3%, bank 2 7.7%, bank 5 1.8%,
  bank 1 untraced.
- Scrapyard Dog: bank 6 59.7%, bank 7 19.5%, bank 5 6.2%, bank 4 5.2%, banks 0-3 untraced.
