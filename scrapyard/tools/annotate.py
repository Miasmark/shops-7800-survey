"""annotate.py: add the shop/text findings to scrapyard/annotations.json (idempotent).
Run from the project root: python scrapyard/tools/annotate.py"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "annotations.json")
a = json.load(open(P))

entries = ["f7:D80B", "f7:D878", "f7:D8A1", "f7:D8EA", "f7:D926", "f7:D088", "f7:D767", "f7:D780",
           "f7:D78C", "f7:D7A9", "f6:5E98", "f6:5AD7", "f6:59F7", "f6:5A0B", "b5:B37D", "b5:B3C5",
           "b5:B6F9", "b5:B701", "b5:B70F", "b4:95AF", "b4:9829", "b4:9895", "b4:9015", "b4:906A",
           "f6:5064", "f6:5190", "f7:F221", "f6:5B22", "f6:5133"]
for e in entries:
    if e not in a["entries"]:
        a["entries"].append(e)

labels = {
    "f7:D000": "ShopVector", "f7:D272": "ShopLoop", "f7:D28F": "ShopFrame", "f7:D357": "ShopStick",
    "f7:D36B": "ShopCursorPalette", "f7:D37D": "tbl_CursorPal", "f7:D380": "tbl_ItemAmount",
    "f7:D388": "tbl_ItemKind", "f7:D2FB": "ShopBuy", "f7:D32F": "ShopRecycle",
    "f7:D5F0": "HudDrawAll", "f7:D613": "HudRefreshOne", "f7:D78C": "HexToAscii2",
    "f7:D767": "BlankLeadingZeros", "f7:D780": "CopyDigitsToRow", "f7:D7A9": "Put99",
    "f7:D7BB": "txt_HexDigits", "f7:D80B": "MsgTick", "f7:D878": "MsgClearWindow",
    "f7:D894": "MsgRowPtr", "f7:D8A1": "MsgStart", "f7:D8EA": "MsgLevelName", "f7:D926": "MsgSkip",
    "f7:D94B": "tbl_MsgPtr", "f7:DFAB": "tbl_MsgWindow", "f7:F007": "SoundRequest",
    "f7:F029": "ENTRY_Nmi", "f6:5F35": "CounterAdd", "f6:5F57": "CounterSpend",
    "f6:5F49": "CounterIndex", "f6:5F25": "tbl_PickupAmount", "f6:5F2D": "tbl_PickupKind",
    "f6:48C8": "DoorEnter", "f6:4988": "DoorHandlerJmp", "f6:4844": "DoorReturn",
    "f6:5E98": "PickupTouch", "f6:5064": "TriggerDispatch", "f6:6357": "ReadStick",
    "f6:4513": "WaitTick", "f6:4536": "WaitFrame", "f6:4209": "GameOverContinue",
    "b5:B000": "ShopSetup", "b5:B063": "ShopItemPalette", "b5:B080": "tbl_ItemPalIdx",
    "b5:B088": "tbl_ItemPal", "b5:B094": "ShopItemPicture", "b5:B0CC": "ShopPicStore6",
    "b5:B0DF": "tbl_ItemPicPtrs", "b5:B11F": "ShopItemLine", "b5:B149": "tbl_ShopLinePtr",
    "b5:B1A9": "txt_ShopLines", "b5:B37D": "ShopLoadPrices", "b5:B395": "tbl_Prices",
    "b5:B3C5": "ShopCopyLists", "b5:B3F2": "tpl_ShopDLL", "b5:B455": "tpl_ShopLists",
    "b5:B718": "tbl_ShopRegionModes", "b4:9604": "txt_Letter", "b4:95AF": "LetterScreen",
    "b4:9086": "txt_Difficulty", "b4:90AE": "txt_Copyright", "b4:98DB": "txt_WorldLevel",
    "b4:9829": "WorldLevelCard",
}
a["labels"].update(labels)

ram = {
    "2227": "World", "2224": "Stage", "2223": "BankShadow", "222E": "PlayerIdx", "25B1": "DoorParam",
    "25AC": "DoorRec", "2497": "ShopChoice", "2496": "ShopNagTimer", "1FAD": "ShopLineRow",
    "1FDD": "ShopPrices", "22A5": "CntMoneyLo", "22B3": "CntMoneyHi", "22A7": "CntCansLo",
    "22B5": "CntCansHi", "22A9": "CntMagicLo", "22AB": "CntBombsLo", "22AD": "CntTimeLo",
    "22BB": "CntTimeHi", "22AF": "CntLives", "22B1": "CntShield", "221B": "Continues",
    "2489": "MsgPtrLo", "248A": "MsgPtrHi", "248B": "MsgIndex", "248C": "MsgCol", "248D": "MsgRow",
    "248E": "MsgWinWidth", "248F": "MsgWinRows", "2487": "MsgDelay", "2488": "MsgSpeed",
    "2486": "MsgBusy", "2481": "HudVisible", "1F5D": "HudRow0", "1F85": "HudRow1",
    "0076": "DliCount", "0074": "FrameCount", "0077": "TickCount", "008C": "ShopItem",
}
a["ram"].update(ram)

comments = {
    "f7:D2D6": "INPT1 (player 2: INPT3): button edge, bit 7 set = down",
    "f7:D2EC": "item $70 = CONTINUE: return carry = choice",
    "f7:D307": "money low < price and money high = 0: can't afford, message $26",
    "f7:D31E": "CounterSpend(kind 0 money, price)",
    "f7:D329": "CounterAdd(tbl_ItemKind[item], tbl_ItemAmount[item])",
    "f7:D2BE": "leave when the level clock is under 3",
    "f7:D82F": "next message byte: 00 end, bit 7 speed, $60 wait, $0D new line, else a character",
    "f6:4911": "copy the door's 6-byte record to $25AC-$25B1",
    "f6:4988": "JMP (handler): the table at ($9002) of the bank named in the record; shop records name bank 0, whose entry 0 is $D000",
    "f7:F084": "the NMI switches to bank 5 (sound) and restores BankShadow at F0CF",
    "b5:B140": "copy the item's 26-character line to ShopLineRow",
}
a["comments"].update(comments)

blocks = [
    {"loc": "f7:D94B", "len": 84, "note": "42 message pointers (word each)"},
    {"loc": "f7:D99F", "end": "f7:DFAA", "note": "messages: style byte, ASCII, $0D new line, bit 7 = speed, $60 = wait a tick, $00 end"},
    {"loc": "f7:DFAB", "len": 16, "note": "message windows, 8 bytes: width, rows, row pointers"},
    {"loc": "f7:D37D", "len": 19, "note": "cursor palette pair, item amounts (BCD), item counter kinds"},
    {"loc": "b5:B080", "len": 20, "note": "item -> palette set index, 4 palette sets of 3 colours (P4)"},
    {"loc": "b5:B0DF", "len": 64, "note": "per item 8 bytes: three (lo,hi) picture rows for the shelf object, 2 spare"},
    {"loc": "b5:B149", "len": 96, "note": "6 worlds x 8 items: pointer to a 26-byte line"},
    {"loc": "b5:B1A9", "len": 468, "note": "18 distinct shop lines, 26 bytes each, ASCII; $02 coin, $03 can"},
    {"loc": "b5:B395", "len": 48, "note": "prices, BCD, 6 worlds x 8 items"},
    {"loc": "b5:B3F2", "len": 99, "note": "shop DLL template (33 zones), copied to $1800"},
    {"loc": "b5:B455", "len": 676, "note": "shop display lists, copied to $1A00-$1CA3"},
    {"loc": "b5:B718", "len": 4, "note": "read mode per screen region (DLI n): 3,0,3,0"},
    {"loc": "b4:9604", "len": 144, "note": "the opening letter, 6 rows x 24, letter font ($5F space)"},
    {"loc": "b4:9086", "len": 40, "note": "difficulty names, 10 bytes each"},
    {"loc": "b4:90AE", "len": 37, "note": "copyright line"},
    {"loc": "b4:98DB", "len": 23, "note": "-- WORLD # LEVEL # --"},
    {"loc": "f6:5F25", "len": 16, "note": "pickup amounts (BCD) and counter kinds for object types $30-$37"},
]
have = {b["loc"] for b in a["blocks"]}
for b in blocks:
    if b["loc"] not in have:
        a["blocks"].append(b)

json.dump(a, open(P, "w"), indent=2)
print("ok", len(a["entries"]), "entries", len(a["labels"]), "labels", len(a["blocks"]), "blocks")
