"""annotate.py: add what was learned about Fatal Run's shop, ticker and passwords to
fatalrun/annotations.json (labels, RAM names, headers, data blocks). Idempotent.
Run from the project folder: python fatalrun/tools/annotate.py ; then disasm.py and verify.py."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(os.path.dirname(HERE), "annotations.json")
a = json.load(open(P))

labels = {
    # fixed bank: flow
    "f7:D0E3": "StageEnd_ToTownAndShop",
    "f7:D153": "BlankScreen_WaitVblank",
    "f7:D185": "Ending_Bank2",
    "f7:D1CA": "StageStart",
    "f7:D344": "PlayLoop_Top",
    "f7:FD94": "DLI_PlayBottom_SoundBank4",
    # bank 6: the shop's DLI chain
    "f6:5603": "ShopDLI_0_FrameFlag",
    "f6:5614": "ShopDLI_1_Pal56",
    "f6:5649": "ShopDLI_2_Pal1234",
    "f6:56A0": "ShopDLI_3_TextMode",
    "f6:56B6": "ShopDLI_4_Bank4Font_HoldInNMI",
    "f6:5753": "ShopDLI_5_PanelEnd",
    # bank 0: the shop
    "b0:B000": "Shop_Entry",
    "b0:B246": "Shop_Frame",
    "b0:B354": "Shop_MoveX",
    "b0:B37E": "Shop_CursorObject",
    "b0:B420": "Shop_HoverAndPrint",
    "b0:B446": "Shop_Buttons_Every16",
    "b0:B4DA": "Shop_CopyListTemplates",
    "b0:B5E1": "Shop_PrintNameAndType",
    "b0:B64C": "Shop_HoverShelf",
    "b0:B679": "Shop_Hover",
    "b0:B69C": "Shop_PrintMoney",
    "b0:B6F2": "Shop_PrintCostLine",
    "b0:B74F": "Shop_ReadButtons",
    "b0:B762": "Shop_Button1_BuyOrRepair",
    "b0:B775": "Shop_Button2_Undo",
    "b0:B77D": "Shop_HideShelfObject",
    "b0:B7A6": "Shop_ShowShelfObject_Undo",
    "b0:B7DF": "Shop_PrintAmountOrStatus",
    "b0:B936": "Shop_Repair",
    "b0:B9A4": "Shop_RepairPay",
    "b0:B9F7": "Shop_UndoDispatch",
    "b0:BB2F": "Shop_CanAfford",
    "b0:BB50": "Shop_Pay",
    "b0:BD09": "Shop_Refund",
    "b0:BD31": "Shop_PrintCostDigits",
    "b0:BD5E": "Shop_PrintByteDecimal",
    "b0:BDEC": "Shop_PrintBCD4",
    "b0:BE91": "Shop_LoadWorkingCopy",
    "b0:BFAE": "Shop_ListSlotPointer",
    "b0:9046": "Shop_BuyDispatch",
    "b0:9F4D": "Shop_Quit_Commit",
    "b0:98B4": "Shop_NamePtrs",
    "b0:9878": "Shop_AsciiToTile",
    "b0:9C0D": "Shop_Prices",
    "b0:9C33": "Shop_BuyHandlers",
    "b0:9C59": "Shop_UndoHandlers",
    "b0:9E39": "Shop_RepairPrices",
    "b0:9AAD": "Shop_TypeListPtrs",
    # bank 4: ticker, passwords
    "b4:A3CB": "Ticker_NextWord",
    "b4:A3EA": "Ticker_Scroll",
    "b4:A4F8": "Ticker_SetMessage",
    "b4:AA31": "Ticker_MessageTokens",
    "b4:AAE0": "Ticker_Words",
    "b4:AD9C": "Ticker_AsciiToTile",
    "b4:BCC0": "Password_Enter",
    "b4:BD1A": "Password_Match",
    "b4:BF01": "Password_Words",
    "b4:BF79": "Password_ShowInShop",
}
ram = {
    "0049": "stage",
    "0048": "cheat_and_mode_flags",
    "00F4": "bank_shadow",
    "0083": "shop_cursor_row",
    "0084": "shop_cursor_line",
    "0085": "shop_cursor_x",
    "0087": "shop_hover_item",
    "008E": "shop_hover_type",
    "008F": "shop_cost_hi",
    "0090": "shop_cost_lo",
    "1802": "shop_money_hi",
    "1803": "shop_money_lo",
    "27F4": "money_hi",
    "27F5": "money_lo",
    "27F6": "ticker_message",
    "27F7": "ticker_token_index",
    "27F8": "ticker_char_index",
    "2292": "work_condition",
    "2261": "car_condition",
    "22BF": "shop_stock",
    "22D0": "shop_type_offered",
    "22AC": "work_type",
    "1C2A": "shop_shelf_hover_map",
    "1CD2": "shop_stock_slots",
}
headers = {
    "b0:B000": "The shop. In: A = bonus (BCD, hundreds), Y = 0, X = flags. Builds the screen from ROM templates, then loops at Shop_Frame until QUIT.",
    "b0:B679": "Hover: which item is under the cursor. Rows 0-5 use the RAM map shop_shelf_hover_map (6 rows x 28 cells of 4 pixels); rows 19+ with x < $50 use the car map through the pointers at $9A15.",
    "b0:9F4D": "QUIT: commit the working copy (condition, counts, types, money) to the game's own state.",
    "f6:56B6": "Switches bank 4 in for the text panel's font (CHARBASE $B0), runs the sound tick and the password line, then waits INSIDE the interrupt until the next DLI (ShopDLI_5) sets $72, and switches bank 0 back.",
    "b4:A3EA": "The HUD ticker: every 4th frame the 18-character row at $2472 moves left one character and the next letter of the current word enters at $2484.",
}
blocks = [
    {"loc": "b0:98B4", "len": 38, "note": "19 item name pointers"},
    {"loc": "b0:98DA", "len": 170, "note": "17 item names, 10 ASCII bytes each"},
    {"loc": "b0:9AAD", "len": 38, "note": "19 pointers to lists of four type-name pointers"},
    {"loc": "b0:9C0D", "len": 38, "note": "19 prices, BCD low byte then high byte"},
    {"loc": "b0:9C33", "len": 38, "note": "19 buy handlers (button 1)"},
    {"loc": "b0:9C59", "len": 38, "note": "19 undo handlers (button 2)"},
    {"loc": "b0:9E39", "len": 38, "note": "19 repair prices, BCD low then high"},
    {"loc": "b4:AA32", "end": "b4:AADF", "note": "ticker messages: word offsets into Ticker_Words, zero ends a message"},
    {"loc": "b4:AAE0", "end": "b4:ABDE", "note": "ticker word list, ASCII, zero-terminated"},
    {"loc": "b4:ABDF", "end": "b4:AC9E", "note": "credits ticker text"},
    {"loc": "b4:AC9F", "end": "b4:AD9B", "note": "story ticker text"},
    {"loc": "b4:BF01", "len": 120, "note": "14 password words and PASSWORD, 8 tile codes each"},
]
a.setdefault("labels", {}).update(labels)
a.setdefault("ram", {}).update(ram)
a.setdefault("headers", {}).update(headers)
have = {b["loc"] for b in a.setdefault("blocks", [])}
for b in blocks:
    if b["loc"] not in have:
        a["blocks"].append(b)
a.setdefault("notes", {})["b0"] = "Bank 0: the shop (code $B000-$BFFF and $9000-$9059, $9F4D; data $8AF0-$9FFF; shelf graphics $8000-$8AFF)."
a["notes"]["b4"] = "Bank 4: title, password entry, high scores, HUD ticker, sound tick ($A003/$A006), the 4-pixel text font at $B000-$B7FF."
json.dump(a, open(P, "w"), indent=1)
print("annotations updated:", len(a["labels"]), "labels,", len(a["blocks"]), "blocks")
