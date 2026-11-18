# Shops, menus and text screens in two retail 7800 games: findings

Project: `disassemblies/shops-7800-survey`. ROM copies: `roms/fatalrun.a78`, `roms/scrapyard.a78`
(both 128K SuperGame: bank 7 fixed at `$C000`, bank 6 also at `$4000`, `$8000-$BFFF` switched).
Addresses are `bank:address` as the CPU sees them (`6:` = bank 6 at `$4000`, `7:` = bank 7 at
`$C000`, `0:`-`5:` in the `$8000` window). Tags: **live** (seen in MAME: a tap, a trace, a RAM
diff, a poke that changed behaviour), **code** (read from the listing or bytes only), **hint**
(a guess). Runs are in `<game>/runs/<name>`.

Part 1 is Fatal Run, part 2 is Scrapyard Dog.

# Part 1. Fatal Run (Atari / Sculptured Software, 1990)

## Summary

- Between stages the game shows a town screen (bank 3), then **one shop screen** (bank 0): a
  free-moving pointer over a wall of goods and over a picture of the car. Pointing shows name,
  type, cost and amount; button 1 buys or repairs, button 2 undoes a purchase, QUIT leaves.
- In-game messages are **word tokens**: one byte a word, into a shared word list. Shop text is
  ASCII in fixed 10-byte fields behind pointer tables. All ASCII is translated to font columns
  when printed.
- Items are tables for display (name, types, price, repair price, stock) but **code for effect**:
  19 buy handlers and 19 undo handlers.
- The password is a **fixed word per four stages**, shown in the shop. It encodes no state.

## How the shop was reached (read before trusting "live")

- Holding "up" from the start drives off the road at the first bend, so the stage end was
  **forced**: `$22B9=07, $22AF=C0` poked at frame 340. That is the game's own test at `7:D353`
  (position high byte 7, low byte >= `$C0`), which jumps to `7:D0E3`. Everything after that is
  the game's own code. A button press at frame 650 skips the town screen; the shop is up by
  frame 795 (runs `end1`, `skip1`).
- For a fourth-stage shop (password line, the TV on the wall) `$49=03` was poked at frame 330,
  so the stage count became 4 (run `pw1`).
- Money was poked (`$1802/$1803`) only for the can't-afford test (run `poor1`).

## 1. Text storage

Inventory with every string decoded: `fatalrun/text_inventory.txt` (`tools/fr_inventory.py`).

| Text | Where | Format | Bytes | Evidence |
|---|---|---|---|---|
| Ticker word list (28 words) | `4:AAE0-4:ABDE` | ASCII, zero-terminated | 255 | live (MISSILES) |
| Ticker messages (56 records) | `4:AA32-4:AADF` | one byte a word (offset into the word list), zero ends | 174 | live for index `$91`, code for the rest |
| Credits ticker | `4:ABDF` | one ASCII string, `(` `)` are special glyphs | 192 | code |
| Story ticker | `4:AC9F` | one ASCII string | 253 | code |
| Shop item names (17) | `0:98DA`, pointers `0:98B4` (19) | 10 ASCII bytes, centred with spaces | 170 + 38 | live |
| Shop type names (25) | `0:9ADB-0:9C04`, pointers `0:9AAD` (19, to lists of four pointers) | 10 ASCII bytes | 250 + 102 | live (DRUM, DISC, 10 GAGE) |
| Shop headings | `0:948E` (COST, AMOUNT, STATUS, blank), `0:8FF1` (BONUS), `0:8BF4` (digits) | ASCII | 49 | live |
| ASCII-to-tile tables | `0:9878` (shop), `4:AD9C` (ticker) | indexed by ASCII - `$20` | 60 + 59 | live (read taps) |
| Password words (14) and PASSWORD | `4:BF01` | 8 tile codes each, already translated | 120 | live (EAGLE1) |
| ALIVE / PERISHED / BONUS | `6:559A` | tile codes | 18 | live on screen |
| NEW GAME / CONTINUE | `4:BBB8` | ASCII | 16 | on screen |
| GAME OVER, high score headings | `4:9E4A`, `4:9FAC` | tile codes | about 51 | code |

Total about 1,807 bytes, tables included. No ending text was found by search (hint: the ending
was not reached).

Tile codes are the font's column numbers: letters `$50-$69`, digits `$00,$08,...,$48`, blank
`$7B`, `$78 $79` the dollar sign. Text that never changes (passwords, labels) is stored already
translated; the rest is ASCII and goes through the 60-byte table at print time.

### The ticker: messages as word tokens (`4:A3CB`, `4:A3EA`)

- The HUD has one 18-character row at `$2472-$2483`. Every fourth frame the row moves left one
  character and the next letter enters at `$2484` (`4:A403`, `4:A454`). In between, the object's
  x moves a pixel a frame from the table at `4:AA2E` (`0A 09 08 07`), so the scroll is smooth
  (code).
- A message is a run of word offsets: `01 A5 AC 00` is GENERAL DAMAGE HIGH, `36 BE BA 00` is FUEL
  LEVEL LOW, `4B 92 00` is MISSILES OBTAINED. `$27F7` indexes the tokens, `$27F8` the letters of
  the current word. A zero letter ends the word and prints a space; a zero token ends the
  message (`4:A3CB-4:A3E9`, `4:A422-4:A44D`).
- Message records are fixed size inside a group (4 bytes for three-word messages, 3 for two-word
  ones), so the start index is group base + record size x number (`4:A370-4:A388`, bases at
  `4:A320`; code).
- Message numbers `$CC` and `$CE` skip the tokens and read the credits and story strings
  directly (`4:A428-4:A43E`).
- **Measured:** the 56 messages spelled out would be 1,014 bytes. Stored they are 174 token bytes
  + 255 bytes of words = 429 bytes (58% less). The token stepping is about 31 bytes of code; the
  whole ticker (scroll, word stepping, translation) is 141 bytes (`4:A3CB-4:A457`).
- Live (run `tick1`): at frame 1978 `4:A388` wrote token index `$91`; then `4:A454` put
  M-I-S-S-I-L-E-S into `$2484`, one letter per four frames.

### Shop text

- Every name is a 10-byte field, centred by hand with spaces: 134 of the 420 field bytes are
  padding (32%).
- A field is shared by pointing at it twice: ARMOR is an item name and also the fourth type of
  WINDSHIELD and BUMPER; PROTECTIVE serves two items; DYNAMITE serves items `$0D` and `$0E`.
- Printing is the same 14-byte loop written inline 14 times in bank 0 (load, subtract `$20`,
  look up `0:9878`, store to the row): about 200 bytes that one subroutine would replace (code).
- The page for one hovered item is name 10 + type 10 + COST 4 + AMOUNT or STATUS 6 characters,
  plus digits made at run time. All 19 items with four types each cost 669 bytes with tables.

## 2. The shop as data

Item numbers: 1 TIRES, 2 OIL, 3 GAS TANK, 4 BRAKES, 5 ENGINE, 6 FUEL, 7 SHIELD, 8 GUN AMMO,
9 ARMOR, `$A` WINDSHIELD, `$B` BUMPER, `$C` DIAMOND, `$D/$E` DYNAMITE, `$F` ROCKET, `$10` NITRO,
`$11` GENERAL (repair only), `$12` SMOKE.

| Table | Where | Record | Evidence |
|---|---|---|---|
| name pointer | `0:98B4` | word per item | live |
| type list pointer | `0:9AAD` | word per item, to four name pointers (level 0-3) | live |
| price | `0:9C0D` | BCD, low byte then high (BRAKES `50 02` = $250) | live |
| repair price | `0:9E39` | BCD, low then high (ARMOR $50) | live on screen |
| condition index | `0:9E5F` | item to offset in the condition block `$2292` | code |
| stock index | `0:9E72` | item to offset in the stock counters `$22BF` | code |
| buy handler | `0:9C33` | code address per item, called by `JMP ($1800)` from `0:9046` | live |
| undo handler | `0:9C59` | code address per item, from `0:B9F7` | live |
| shelf object | `0:9848` (12 list addresses), `0:99BC` (4-byte header per item), `0:9A02` (palette bits per item) | | code |
| stock slots | `0:99A5` (12 default items), `0:99B1` (the three special slots), `0:99B4` (8 special items) | | live (RAM `$1CD2`) |
| availability | `0:9984` | one mask byte per stage, ANDed with a random byte; up to three special items get a slot | code; live for the result |
| type offered | `0:9DD9-0:9E38` | six tables of 16 (stage / 2), the last holds two 2-bit fields in a byte | live (DRUM at stage 1, DISC at stage 4) |
| hover map, wall | `0:9A99` (pointer per town) | 6 rows x 28 cells, item number, or bit 7 + slot number | live |
| hover map, car | `0:9A15` (5 row pointers) | 20 cells a row, part number | live on screen |

### Pointer and hover

- The pointer is a row `$83` (0-23), a line in the row `$84` (0-7) and an x `$85` (0-`$9C`). The
  stick moves one line or one pixel a frame (`0:B2E1-0:B37C`; live: the row steps every 8
  frames).
- At entry the wall's hover map is copied from ROM to RAM `$1C2A` (168 bytes). A byte with bit 7
  set is a **placeholder**: its low bits pick one of the three special slots, and the item drawn
  for that slot this visit is stored instead (`0:B154-0:B166`). Live: RAM rows hold `01` TIRES,
  `03`, `04`, `05`, `06`, `08`, `09`, `0A`, `0B` and, in that visit, `12` SMOKE and `10` NITRO
  (run `pw1`, dump at frame 850).
- Each frame `0:B679` reads the item under the pointer: rows 0-5 with x in `$1A-$87` use the RAM
  map at `(x - $1A) / 4`; rows 19+ with x < `$50` use the car map. The result is `$87`, 0 for
  nothing. Live: sweeping the pointer gave `$87` = 04, 03, 12, 01, 05, 06, 08, 09 in turn.
- QUIT is a region test, not an item: row >= `$17`, x >= `$80` and button 1 (`0:B4B4`).

### Money, prices, digits

- Money is two BCD bytes (four digits). At entry: carried money `$27F4/$27F5` + bonus, added
  with `SED`, set to 9999 on overflow or when a cheat bit is set (`0:B04A-0:B068`).
- `0:B69C` prints money each frame: each nibble indexes the string `0123456789` (`0:8BF4`), then
  the ASCII-to-tile table. `0:BDEC` prints a BCD price the same way and blanks leading zeros;
  `0:BD31` right-aligns it after the two-tile dollar sign.
- Stock counts and percentages are binary. `0:BD5E` turns a byte (0-100) into BCD by adding a
  BCD weight from `0:8FEA` for each set bit, under `SED`: no division (code).

### Buying, undoing, repairing

- Buttons are read once every 16 frames (`0:B446`), so a held button repeats slowly.
- Button 1 (`INPT1`) on the wall: `0:9046` jumps to the item's buy handler. Each handler calls
  `0:BB2F` (money >= price, carry set), checks the stock counter, sets the working copy's
  condition bytes to `$FF` and its type byte to the type on offer, decrements the stock, and
  pays through `0:BB50` (BCD subtract). There are 19 buy and 19 undo handlers, about 700 bytes
  (`0:BA0A-0:BD08` less three helpers).
- Live (run `buy1`): BRAKES at $250: money $2000 to $1750, stock `$22C0` 1 to 0, AMOUNT 1 to 0,
  and the brake picture left the wall.
- **Can't afford is silent**: `0:BB2F` returns carry clear and the handler returns. Live (run
  `poor1`): with $100, button held 30 frames, no write to money or stock; with $250 poked in,
  the purchase went through at frame 953 (writes at `0:BA8F`, `0:BB5C`, `0:BB70`).
- Button 2 (`INPT0`): `0:B7A6` finds the item's shelf object; if it is marked sold, it restores
  the object's palette and jumps to the undo handler, which restores stock, refunds
  (`0:BD09`) and copies condition and type back from the committed state. Live: money back to
  $2000, stock 1, picture back (frame 992).
- "Sold" is shown by `ORA #$E0` on the object header's palette bits (`0:B7A1`), so the object
  draws in a palette that hides it. No list is rebuilt (code; the object vanishing is live).
- Over the car (rows 7+): button 1 repairs. `0:B936` picks the part's condition byte, `0:B9A4`
  takes the repair price and adds 20 to the condition, to a ceiling (code; "ARMOR 10 GAGE COST
  $50 STATUS 100%" seen live).
- The shop works on a **working copy**: `0:BE91` copies condition (16 bytes), counts (9) and
  types into `$2292-$22B8` at entry; QUIT (`0:9F4D`) copies them back and stores the money.
  Live: `$27F4/$27F5` = `20 00` written at the QUIT frame.

## 3. How the screen is drawn

- DLL template `0:BE50` (91 bytes) copied to `$180C`; list templates copied blind, 256 bytes
  each, from `0:91FF`, `0:9309`, `0:93C3` to `$186B`, `$1975`, `$1A2F` (`0:B4DA`), then poked.
  Live: the DLL at `$180C` decodes with `dlwalk.py` (run `skip1`, dump at frame 1100).
- Top: 9 zones of 16 lines. The wall is two indirect objects of 10 two-byte characters a zone
  (CTRL `$58`, CHARBASE `$80`, tiles in bank 0), from a 20 x 9 map in RAM at `$1AE3`.
- The map is built in two steps: a common 180-byte layout (`0:9073`) overlaid by a per-town one
  (pointer `0:8FF6`, first 80 bytes, zero = keep), then material codes below `$16` translated
  through a per-town tile table (pointer `0:8DF0`). Four towns look different from the same
  layout (`0:B06C-0:B128`; RAM maps live).
- Goods, shopkeeper and customers are direct 160A objects over the map. The pointer is one
  object written into two zones; its graphics pointer comes from a table by (row kind, line)
  (`0:97B8`, `0:97F8`).
- Bottom: 6 zones of 8 lines with one-byte characters 4 pixels wide (CTRL `$48`, CHARBASE `$B0`).
  The text rows are RAM: `$1C16` name, `$1C06` type, `$1C20` COST, `$1BF6` price, `$1C24`
  AMOUNT or STATUS, `$1BF1` amount, `$1BFC` BONUS, `$1C12` money, `$1CEF/$1CE6` PASSWORD and
  its word. Name, type, price, amount and money are **rewritten every frame** whether or not
  anything changed (`0:B420`).
- The 4-pixel font is in **bank 4** (`$B000-$B7FF`), not bank 0. DLI `6:56B6` switches bank 4 in
  at the top of the text panel, loads palettes, runs the sound tick (`4:A006`) and the password
  line (`4:B809`), then **waits inside the interrupt** (`6:573C`) until the next DLI (`6:5753`)
  sets `$72`, and switches bank 0 back. The main program, which lives in bank 0, cannot run
  while bank 4 is in. Live: `6:56B9`, `4:BF79`, `6:573C`, `6:5742` all executed in shop frames;
  CHARBASE written `$B0` then `$80` each frame.
- Palettes: a RAM shadow at `$0140-$0189` uploaded by a chain of six DLIs (`6:5603`, `6:5614`,
  `6:5649`, `6:56A0`, `6:56B6`, `6:5753`), three registers per WSYNC.
- On every fourth stage five-byte objects from `0:947E` add a TV to the wall, animated from
  frame tables at `0:8AF0`, `0:8CF0`, `0:8EF8` (live on screen).

## 4. Item effects in play

- The car is a stats block: 16 condition bytes `$2261-$2270` (four tyres, four brakes, engine,
  tank and so on, `$FF` = new), counts `$2273-$227B`, type levels `$2281-$228C` (0-3).
- A purchase sets condition to `$FF` and stores the type level; play uses the type as a table
  index (engine type `$228A` indexes `6:6F8B` at `6:6EA8`; tank type indexes the capacity table
  `0:B90D` = `$20,$10,$0A,$08`) (code, two sites read).
- The effect itself is per-item code, not data (section 2).

## 5. Screen flow and banking

- `7:D0E3` (stage end): fade, then bank 3 `$B000` with Y = 0 (town screen; returns the bonus),
  stage + 1, bank 0 `$B000` (shop), bank 3 `$B000` with Y = `$80` (leaving town), then
  `7:D1CA` (stage start: bank 4 `$A000`, bank 5 `$9BE3`). Stage `$1F` goes to bank 2 `$B000`
  (ending) instead. Live: bank shadow `$F4` went 5, 3, 0, 3, 5 (runs `end1`, `buy1`).
- Banks: 0 shop; 1 data (untraced); 2 ending; 3 town screens; 4 title, passwords, high scores,
  ticker, sound tick, text font (jump tables at `$A000` and `$B800`); 5 play data and set-up;
  6-7 engine and all interrupt handlers.
- Each screen bank has its entry at `$B000`; the fixed bank writes the register, then the shadow
  `$F4` (register first: a one-instruction race, as in the skills' notes on Motor Psycho).
- The play screen's NMI also switches banks: `7:FDA4` selects bank 4 for the sound tick and
  restores from `$F4` (`7:FDB4`).
- The shop sets two-button mode itself: `LDA #$14 / STA SWBCNT` at `0:B00C`, unconditional.

## 6. Passwords

- `4:BF01`: 14 words of 8 tile codes. Words 0-7 (EAGLE1, ZEBRA, LYNX, HORNET8, DOLPHIN,
  GORILLAS, TURTLE, ATOMIC) start the game at stage 4, 8, ... 32: `4:BD41` returns
  (index + 1) x 4. Words 8-13 (CREDITS, ASSETS, MUTATE, CONQUER, POWERFUL, FORTIFY) OR a bit
  from `4:BD6B` into the flags byte `$48` (ASSETS and FORTIFY make shop money 9999, `0:B04A`).
- The check is a plain compare of the eight typed codes against each word, last to first
  (`4:BD1A-4:BD37`). Nothing about the car or money is encoded: a continue starts with a
  standard car (code).
- The word is shown in the shop on every fourth stage: `4:BF79` copies PASSWORD and word
  (stage / 4 - 1) into the panel's rows and moves the two objects on screen by writing x `$7F`.
  Live: stage 4 showed PASSWORD EAGLE1; RAM `$1CE6` held its codes.
- Entry runs from RAM (`JSR $254B` at `4:BD12`); not read.

## 7. Other things

- The `.log` beside the ROM in the library is a TIA sound capture (`probes/audio.lua` format:
  frame, AUDC/AUDF/AUDV of both voices), not a trace.
- The story is never a page: it is one 253-byte string fed through the 18-character ticker.
- The town screen's labels and the passwords skip the translation table by being stored as tile
  codes.

## Dead ends and corrections (Fatal Run)

- The text font at CHARBASE `$B0` looked impossible (bank 0 has the shop's code at `$B000`). It
  is bank 4, switched in by the DLI.
- A run that missed the stage-end poke showed `6:7DCA` writing `$1802/$1803`: outside the shop
  those bytes belong to the play screen. They are money only while the shop runs.
- Read taps reported `0:B256` and `0:B262` reading all of `$8AF0-$9FFF`: those are MARIA's
  fetches during two store instructions (pitfalls.md), not readers.
- The tracer prints bank 2's and bank 3's `$B000` entries as `sub0_B000` in bank 7's listing.

## Coverage and limits (Fatal Run)

- Listing round-trips. Bank 6 45.5%, bank 7 45.5%, bank 4 31.5%, bank 0 25.8% (the shop's code
  `$B000-$BFD0` is fully traced), bank 3 12.3%, bank 2 7.7%, bank 5 1.8%, bank 1 untraced.
- Not determined: the town screen's bonus arithmetic; the password entry routine; the ending;
  what each cheat bit does in play; most uses of the type bytes in play.

# Part 2. Scrapyard Dog (Atari, 1990)

## Summary

- The game has **one shop screen**, used for every shop and for the continue prompt. A shop sells
  **one item**: the page is chosen by one byte (`$25B1`, item in the high nibble) and everything
  else is looked up. The player answers NAH! or YEAH!.
- Text is **plain ASCII, one byte a letter**, nothing packed. The only economies are a pointer
  table sharing whole lines between worlds, a new-line code with automatic wrap, and speed/hold
  codes inside the message stream.
- No passwords. A game over offers one of three free continues through the shop page.

## How the shop was reached (read before trusting "live")

- **Entry was forced.** For one frame the operand of `JSR $4BAA` at `6:4390` (level loop) was read
  as `$48C8`, the door routine, with `$EF` (door number) poked to 6 and `$EC/$ED` (return position)
  poked. From there the game's own code ran: it copied bank 0's own door record 6
  (`00 FF 3F 00 00 01` at `0:9102`) and jumped through bank 0's handler table to `7:D000`, the shop.
  Probe `tools/sd_patch.lua` (`PATCH`); runs `shop6`, `buy6`.
- For other pages the byte written to `$25B1` was replaced by a write tap (`SUBST`), the world by a
  poke of `$2227`, money by a poke of `$22A5`. Script `tools/sd_items.py`.
- The **continue page needed no forcing**: lives (`$22AF`) poked to 0 and the clock (`$22AD/$22BB`)
  to 2 at frame 700; the game ran its own time-up, game-over and continue path (`runs/gameover`).
- Dead ends:
  - `$22AD/$22BB` looked like a room number; they are the **level clock** in BCD (poking them
    changed the clock, runs `door00`-`door02`).
  - Only one `JSR` to the shop loop exists (`6:4227`, the continue path). Level shops arrive by
    `JMP ($0089)` at `6:4988`.
  - `$25B1`'s real writer is `STA $25AC,X` at `6:4911`, found by a scan for indexed stores
    (`tools/sd_refs.py`).
  - Forcing the PC at a frame end was rejected: level logic is mid-routine at every frame end
    (`runs/pclog/force.txt`).
  - No shop door was found by playing.

## 1. Text storage

| Text | Where | Format | Bytes | Evidence |
|---|---|---|---|---|
| Messages (42: 16 phone calls, 17 level names, 8 shop/bonus, 1 empty) | `7:D99F-7:DFAA`, pointers `7:D94B` | stream, below | 1,548 + 84 | live for `$11`, `$22`, `$26`, `$27`, `$29`; code for the rest |
| Shop lines (18 distinct) | `5:B1A9-5:B37C`, pointers `5:B149` (48 words: 6 worlds x 8 items) | 26 raw bytes, no terminator; `$02` coin, `$03` can | 468 + 96 | live (8 pages of world 1, 2 of world 6) |
| Opening letter | `4:9604-4:9693` | 6 rows x 24 raw bytes in a second alphabet of the same font (`$61-$7A` letters, `$5F` blank, `$5E` apostrophe, `$7E` full stop, `$5C` hyphen) | 144 | code + screenshot `runs/boot1` frame 300 |
| Difficulty names | `4:9086` | 4 x 10 raw bytes | 40 | code |
| Copyright line | `4:90AE` | zero-terminated | 37 | live (RAM `$1F35`) |
| `-- WORLD # LEVEL # --` | `4:98DB` | 23 raw bytes, digits patched in RAM | 23 | live |
| HUD rows | `6:459C` | 2 x 40 raw bytes | 80 | live |
| PAUSED | `6:472B` | 6 bytes | 6 | code |

Total about 2,346 bytes of characters, 180 of pointers. Padding inside that (`tools/sd_pad.py`):
50 centring spaces in messages, 73 of the shop lines' 468 bytes, 23 of the letter's 144. No ending
text was found by search in any bank; the ending was not reached (hint). The full inventory is in
`scrapyard/text_inventory.txt`.

### The message stream (`7:D80B` MsgTick)

- One **window byte** (index into 8-byte records at `7:DFAB`: width, rows, a pointer per row; only
  window 0 is used: 40 x 2 at `$1F5D` and `$1F85`, the HUD's own rows), then:
  - `$20-$5F` a character; the cursor wraps at the window's width, and past the last row the window
    clears and typing restarts;
  - `$0D` new line;
  - bit 7 set: typing speed = low 7 bits, frames a byte;
  - `$60`: types nothing, uses one tick, so `<$C0><$60>` holds 64 frames;
  - `$00`: end, clear the window, redraw the HUD (`7:D5F0`).
- `7:D8A1` MsgStart(A) sets the pointer (`$2489/$248A`), clears the window, speed 4. A button ends a
  phone call early (`6:5AE3`, code).
- Live (`runs/noafford`): message `$26` started at frame 922 with pointer `$DEF1`; `7:D854` stored
  one character every 4 frames, 68 in all; the HUD returned after the hold.
- Code size: 320 bytes for the printer, start, clear, level-name and skip routines. A message costs
  its letters + 1 window byte + 3 ending bytes + 2 pointer bytes.
- The level name's number is computed: `$11 + world*3 + stage` (`7:D907`; code, and live at 1-1).

### Cost of a screen

Shop page 26 + 2 bytes. Letter 144 bytes for 119 visible characters. A two-line message 68-80
bytes. The 96-byte pointer table lets 5 lines serve all 6 worlds; only EXTRA LIFE and ONE HIT
SHIELD, whose prices change, exist six times.

## 2. The shop as data

`$25B1` high nibble: 0 can recycle, 1 regular cans, 2 magic cans, 3 bombs, 4 time, 5 extra life,
6 shield, 7 continue.

| Table | Where | Record | Use |
|---|---|---|---|
| line pointer | `5:B149` | word, `world*8 + item` | line copied to RAM row `$1FAD` by `5:B11F` |
| price | `5:B395` | BCD byte, 6 x 8 | the world's 8 prices copied to `$1FDD` by `5:B37D` |
| shelf picture | `5:B0DF` | 8 bytes: three (lo, hi) pointers, 2 spare | `5:B094` stores each into 6 list slots; item 7 is zeros |
| item colours | `5:B080` (set per item), `5:B088` (4 sets x 3) | | palette 4, by `5:B063` |
| amount gained | `7:D380` | BCD: 00,02,01,01,30,01,01,00 | |
| counter gained | `7:D388` | 0-6 | |

World 1 prices 0, 1, 2, 5, 10, 20, 5, 0; life 20-45 and shield 5-30 over six worlds (live: world 1
all, world 6 life 45 and shield 30).

The price is stored **twice**, as a number and as letters in the line; that is why two items need
12 lines instead of 2 (260 bytes).

Mismatch: item 1's line says `REGULAR CANS - 1 FOR 1` and the tables give 2 cans for 1 coin (live:
cans 5 to 7). No door record in banks 0-2 selects item 1, so the page looks unused (code; bank 3
not read).

### The loop (`7:D272` ShopLoop, 267 bytes, fixed bank)

1. Bank 5 in; draw the HUD; `JSR 5:B000` ShopSetup (palettes, picture pointers, line, prices,
   lists); choice `$2497` = 0; nag timer `$2496` = 6.
2. Each frame (`7:D28F`): stick left/right sets the choice (`7:D357`); cursor colours (`7:D36B`);
   every 64 ticks the nag timer counts, at 0 message `$22` (or `$29` on the continue page); message
   printer; HUD refresh.
3. Leave when the level clock is under 3 (`7:D2BE`).
4. Button edge (`INPT1,X`, bit 7 set = down, `7:D2D6`): item 7 returns carry = choice; NAH!
   returns; item 0 needs cans (else message `$25`), then `CounterSpend(cans,1)`,
   `CounterAdd(money,1)`; others compare money with the price (`7:D304`; message `$26` if short),
   then `CounterSpend(money, price)`, `CounterAdd(kind[item], amount[item])`. The player stays and
   can buy again.

Live: recycle x3 gave cans 5,4,3,2 and money 5,6,7,8 (writers `6:5F60`, `6:5F3C`); item 2 -2/+1;
item 3 -5/+1; item 4 -10, clock 273 to 303; item 5 -20, lives 3 to 4; item 6 -5, shield 1 to 2;
5 coins against 20: nothing changed, message `$26`; NAH! returned to the level at the same place.

### Counters

- 16-bit BCD, low bytes `$22A5 + 2*kind + player`, high bytes `$0E` further: 0 money, 1 cans,
  2 magic cans, 3 bombs, 4 clock, 5 lives, 6 shield (live).
- `6:5F35` CounterAdd(A kind, Y amount), `6:5F57` CounterSpend (clamps at 0), helper `6:5F49`:
  67 bytes. Byte scan: 3 callers of Add, 9 of Spend (code).
- HUD: `7:D78C` BCD byte to two ASCII digits via `7:D7BB`, `7:D767` blanks leading zeros, `7:D780`
  copies into the row; over 99 prints `99` (`7:D7A9`). One field every 4 frames in turn (`7:D613`)
  (code; money changing on screen is live).

### Cursor

Each button has a bar at both sides in palette 6: NAH!'s use colour 1, YEAH!'s colour 2. `7:D36B`
writes `P6C1/P6C2` as (`$47`,`$00`) or (`$00`,`$47`) from `7:D37D`. No list edit (live: writes
`39=47 3A=00` each frame; bars move in screenshots).

## 3. How the screen is drawn

- ROM templates copied with DMA off: DLL `5:B3F2` (99 bytes, 33 zones) to `$1800`, lists `5:B455`
  (676 bytes) to `$1A00-$1CA3` by a blind four-page copy (`5:B3C5`), then 18 picture slots poked
  (live: `runs/shop6/dump_f00900.bin` through `dlwalk.py`).
- One DLI handler counts calls in `$76` and sets `CTRL = ($79 & $FC) | mode[$76]` from a 4-byte RAM
  table at `$F0` each screen fills (`5:B718`: 3,0,3,0): HUD 320A characters, picture 160, text line
  320A characters, buttons 160 (live: CTRL `$4B`,`$48`,`$4B`,`$48`).
- Text is character-mapped, one-byte characters, palette 7, `CHARBASE` `$F8` (set once, `6:4032`):
  HUD rows as two 20-character objects each, the shop line one 26-character object at `$1FAD`.
  `$1F35-$203C` is one pool of character rows every screen reuses (live).
- Picture: 13 zones of 8 lines; wall = a 5-byte strip repeated as 160A objects; shopkeeper = one
  160B object a zone cut to the figure's width (14-24 bytes); item = 16 x 24 pixels, 160B, drawn
  six times; buttons 6-byte 160A objects over two zones (live).
- Palettes: about 20 colour registers set by immediate loads, 83 bytes of code (`5:B003-5:B055`).
- Shop graphics are in bank 5 (`$A000-$A8FF`), so bank 5 stays in for the visit.

## 4. Item effects in play

- A purchase is only `CounterAdd(kind, amount)`: two table bytes an item.
- Level pickups use the same shape: object types `$30-$37` index amounts `6:5F25`
  (01,01,01,01,30,01,01,10) and kinds `6:5F2D`, then `JSR CounterAdd` (`6:5EC0`) (code).
- Play reads the counters where needed (shield at `6:5EE2`; code, one site read).

## 5. Screen flow and banking

- Banks: 0-2 the three level kinds, chosen by the stage number (`6:4A4B`); 3 rooms behind doors;
  4 title, letter, difficulty, world card (jump table `4:9000`); 5 sound driver (jump table
  `5:8000`) and the whole shop; 6 the engine; 7 shop loop, HUD, messages, NMI, sound queue, font,
  graphics. Switches seen live: `6:4046` to 5, `6:4051` to 0, `6:4067/4072/40D5` to 4, `6:4A51` and
  `6:4960` to 0, `7:D274` to 5.
- Every switch keeps a shadow (`$2223`). The **NMI switches banks**: on the frame's last DLI it
  selects bank 5, runs sound requests queued by `7:F007`, and restores the shadow (`7:F084`,
  `7:F0CF`; live, 1,093 times in the first trace). ShopLoop writes the register before the shadow
  (`7:D274`, `7:D277`), a one-instruction race (code, not seen).
- Doors are data. `6:48C8` copies a 6-byte record from the level bank's table (pointer at `$9000`)
  to `$25AC-$25B1`: byte 0 bank and handler number; byte 1 `$FF` = code room (switch bank, `JMP`
  through its table at `($9002)`) or an entry position; byte 2 return offset; bytes 3-4 an optional
  trigger; byte 5 the parameter. Shop records are `00 FF 3F 00 00 xx`; bank 0's handler 0 is
  `$D000`, `JMP ShopLoop` (live: tap at `6:4911`, trace `J f6:4988 f7:D000`).
- After setup the loop reads only RAM copies and fixed-bank tables; bank 5 is needed for MARIA's
  graphics and the NMI's sound.
- Level logic runs once per two frames (`6:4513` waits on `$74 AND $FE`); the shop loop every frame
  (live, `runs/pclog`).

## 6. Continues and passwords

- No password screen. `$221B` = 3 at game start (`6:40EA`). At game over `6:4209` decrements it and
  opens the shop page with item 7 and a 20-second clock; YEAH! restarts the level with 3 lives
  (live: `$221B` 3 to 2 at frame 1136, `DECIDE QUICKLY...` typed, YEAH! gave lives 3 and the world
  card).
- Start world and stage come from ROM bytes `6:4000/4001` (both 0): a developer's level select
  (code).

## 7. Other things

- A message hides the HUD (`$2481` = 0) and its end redraws it: no extra zone or RAM for dialogue
  (live).
- The world card's letters fly in: each letter is an object whose x moves one pixel a frame toward
  a target table (`4:98F2`, loop `4:9869-4:9894`) (code; mid-flight in `runs/gameover` frame 1900).
- The shop runs on the level's clock, so browsing costs time.

## Coverage and limits (Scrapyard Dog)

- Listing round-trips. Bank 6 59.7%, bank 7 19.5%, bank 5 6.2%, bank 4 5.2%, banks 0-3 untraced.
- Not determined: where shop doors are in the levels; bank 3's bonus rooms; whether an ending text
  exists; which physical button `INPT1` is.
