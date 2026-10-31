"""RE5 item IDs: ``mItemSet.ItemId`` -> (unit class, readable name)
    item id is use in lot files
"""
ITEM_ID_TO_INFO = {
    256: ("", "Hand-to-Hand"),
    257: ("", "Knife"),
    258: ("uWp02", "M92F"),
    259: ("", "VZ61"),
    260: ("uWp04", "Ithaca M37"),
    261: ("uWp05", "S75"),
    262: ("uWp06", "Hand Grenade"),
    263: ("uWp07", "Incendiary Grenade"),
    264: ("uWp08", "Flash Grenade"),
    265: ("uWp09", "SIG 556"),
    266: ("uWp0a", "Proximity Mines"),
    267: ("uWp0b", "S&W M29"),
    268: ("uWp0c", "Grenade Launcher"),
    269: ("uWp0d", "Rocket Launcher"),
    270: ("", "Knife"),
    271: ("", "Longbow"),
    272: ("uWp10", "H&K P8"),
    273: ("", "SIG P226"),
    274: ("uWp03", "Samurai Edge"),
    275: ("uWp13", "H&K MP5"),
    276: ("uWp1d", ""),
    277: ("", "Gatling Gun"),
    278: ("uWp16", "M3"),
    279: ("uWp17", "Jail Breaker"),
    281: ("", "Hydra"),
    282: ("uWp1a", "L. Hawk"),
    283: ("uWp1b", "S&W M500"),
    284: ("uWp1c", "H&K PSG-1"),
    285: ("uWp20", "AK-74"),
    286: ("", "M93R"),
    287: ("", "Px4"),
    288: ("", "Dragunov SVD"),
    289: ("uWp21", "Flamethrower"),
    290: ("", "Stun Rod"),
    293: ("uWp25", "G. Launcher (EXP)"),
    294: ("", "G. Launcher (ACD)"),
    295: ("", "G. Launcher (ICE)"),
    297: ("", "Samurai Edge"),
    298: ("uWp36", ""),  # egg?
    300: ("uWp3d", ""),  # egg?
    303: ("", "Gun Turret"),
    304: ("uWp30", "Lantern"),
    308: ("uWp34", "L.T.D."),
    309: ("uWp35", "Rocket Launcher (NVS)"),
    310: ("", "Egg (Rotten)"),
    313: ("", "G. Launcher (FLM)"),
    314: ("", "G. Launcher (FLS)"),
    315: ("", "G. Launcher (ELC)"),
    316: ("uWp3c", "Egg (White)"),
    317: ("", "Egg (Brown)"),
    318: ("uWp3e", "Egg (Gold)"),
    336: ("", "Adze"),
    337: ("", "Sickle"),
    338: ("", "Bow Gun"),
    339: ("", "Shovel"),
    340: ("", "Dynamite"),
    341: ("", "Machete"),
    344: ("", "Giant Axe"),
    345: ("", "Steel Pipe"),
    346: ("", "Bottle"),
    347: ("", "Chainsaw"),
    349: ("", "Gatling Gun"),
    350: ("", "Torch"),
    351: ("", "Spear"),
    352: ("", "Shield"),
    354: ("", "Bow"),
    356: ("", "Morning Star"),
    357: ("", "Stun Rod"),
    377: ("uWp79", ""),
    513: ("uIt0201", "Handgun Ammo"),
    514: ("uIt0202", "Machine Gun Ammo"),
    515: ("uIt0203", "Shotgun Ammo"),
    516: ("uIt0204", "Rifle Ammo"),
    518: ("uIt0206", "Explosive Rounds"),
    519: ("uIt0207", "Acid Rounds"),
    520: ("uIt0208", "Nitrogen Rounds"),
    521: ("uIt0209", "Magnum Ammo"),
    526: ("uIt020e", "Flame Rounds"),
    527: ("uIt020f", "Flash Rounds"),
    528: ("", "Electric Rounds"),
    529: ("uIt0211", "RPG Round"),
    769: ("uIt0301", "Herb (Green)"),
    770: ("uIt0302", "Herb (Red)"),
    771: ("", "Herb (X)"),
    772: ("uIt0304", "First Aid Spray"),
    773: ("", "Herb (Green)"),
    774: ("", "Herb (Red)"),
    775: ("", "Herb (G+G)"),
    776: ("", "Herb (G+G+G)"),
    777: ("", "Herb (G+R)"),
    778: ("", "Herb (G+X)"),
    779: ("", "Herb (G+R+X)"),
    780: ("", "Egg (White)"),
    781: ("", "Egg (Brown)"),
    782: ("", "Egg (Gold)"),
    783: ("", "Nile Perch"),
    784: ("uIt0310", "Nile Perch (Big)"),
    785: ("", "Water"),
    786: ("", "Herb (X)"),
    1025: ("uIt0401", "Gold (Large)"),
    1026: ("uIt0402", "Gold (Small)"),
    1027: ("uIt0403", "Gold Bars"),
    1028: ("", "Sapphire"),
    1047: ("uIt0417", "Gold Ring"),
    1048: ("uIt0418", "Dead Bride's Necklace"),
    1049: ("uIt0419", "Venom Fang"),
    1050: ("uIt041a", "Antique Clock"),
    1051: ("uIt041b", "Chalice (Silver)"),
    1052: ("uIt041c", "Chalice (Gold)"),
    1053: ("uIt041d", "Idol (Silver)"),
    1054: ("uIt041e", "Idol (Gold)"),
    1055: ("uIt041f", "Ceremonial Mask"),
    1056: ("uIt0420", "Ivory Relief"),
    1057: ("uIt0421", "Beetle (Brown)"),
    1058: ("uIt0422", "Jewel Beetle"),
    1059: ("", "Royal Necklace"),
    1060: ("uIt0424", "Jewel Bangle"),
    1061: ("uIt0425", "Beetle (Gold)"),
    1062: ("", "Beetle (Emerald Green)"),
    1063: ("uIt0427", "Score Star (Small)"),
    1064: ("uIt0428", "Score Star (Medium)"),
    1065: ("uIt0429", "Score Star (Large)"),
    1104: ("uIt0450", "Topaz (Pear)"),
    1105: ("uIt0451", "Ruby (Pear)"),
    1106: ("uIt0452", "Sapphire (Pear)"),
    1107: ("uIt0453", "Emerald (Pear)"),
    1108: ("uIt0454", "Diamond (Pear)"),
    1111: ("uIt0457", "Topaz (Square)"),
    1112: ("uIt0458", "Ruby (Square)"),
    1113: ("uIt0459", "Sapphire (Square)"),
    1114: ("uIt045a", "Emerald (Square)"),
    1115: ("", "Diamond (Square)"),
    1118: ("uIt045e", "Topaz (Oval)"),
    1119: ("uIt045f", "Ruby (Oval)"),
    1120: ("uIt0460", "Sapphire (Oval)"),
    1121: ("uIt0461", "Emerald (Oval)"),
    1122: ("uIt0462", "Diamond (Oval)"),
    1125: ("uIt0465", "Topaz (Trilliant)"),
    1126: ("uIt0466", "Ruby (Trilliant)"),
    1127: ("uIt0467", "Sapphire (Trilliant)"),
    1128: ("uIt0468", "Emerald (Trilliant)"),
    1129: ("", "Diamond (Trilliant)"),
    1132: ("uIt046c", "Power Stone"),
    1133: ("uIt046d", "Lion Heart"),
    1134: ("uIt046e", "Blue Enigma"),
    1135: ("uIt046f", "Soul Gem"),
    1136: ("", "Heart of Africa"),
    1139: ("", "Topaz (Marquise)"),
    1140: ("uIt0474", "Ruby (Marquise)"),
    1141: ("", "Sapphire (Marquise)"),
    1142: ("uIt0476", "Emerald (Marquise)"),
    1143: ("uIt0477", "Diamond (Marquise)"),
    1146: ("uIt047a", "Topaz (Brilliant)"),
    1147: ("uIt047b", "Ruby (Brilliant)"),
    1148: ("uIt047c", "Sapphire (Brilliant)"),
    1149: ("uIt047d", "Emerald (Brilliant)"),
    1150: ("uIt047e", "Diamond (Brilliant)"),
    1281: ("", "Punisher's Key"),
    1282: ("", "Punisher's Key"),
    1283: ("uIt0503", "Furnace Key"),
    1285: ("", "Execution Ground Key"),
    1286: ("uIt0506", "Port Key"),
    1287: ("uIt0507", "Hangar Keycard A"),
    1288: ("uIt0508", "Hangar Keycard B"),
    1289: ("uIt0509", "Old Building Key"),
    1290: ("uIt050a", "Tanker Keycard A"),
    1294: ("uIt050e", "Sky Emblem"),
    1295: ("uIt050f", "Earth Emblem"),
    1296: ("uIt0510", "Sea Emblem"),
    1298: ("uIt0512", "Shaman Slate"),
    1299: ("uIt0513", "Warrior Slate"),
    1300: ("uIt0514", "Beast Slate"),
    1301: ("uIt0515", "Raptor Slate"),
    1302: ("uIt0516", "Crane Keycard"),
    1303: ("uIt0517", "Tanker Keycard B"),
    1304: ("uIt0518", "Warrior Slate"),
    1306: ("", "Guard's Key"),
    1307: ("uIt051B", "Bridge Keycard"),
    1312: ("uIt0520", "Square Crank"),
    1313: ("uIt0521", "Centaur Emblem"),
    1314: ("uIt0522", "Password 1"),
    1315: ("uIt0523", "Password 2"),
    1316: ("uIt0524", "Password 3"),
    1317: ("uIt0525", "Jail Key"),
    1318: ("uIt0526", "Gold Crest"),
    1319: ("uIt0527", "Silver Crest"),
    1320: ("uIt0528", "Heat-Sensitive Paper"),
    1321: ("uIt0529", "Transport Area Key"),
    1322: ("uIt052a", "Emergency Exit Key"),
    1323: ("uIt052b", "Sun Eater Serpent Shard"),
    1324: ("uIt052c", "Dual-Head Serpent Shard"),
    1325: ("uIt052d", "Serpent Tail Shard"),
    1326: ("uIt052e", "Tri-Head Serpent Shard"),
    1327: ("uIt052f", "Crank (Red)"),
    1328: ("uIt0530", "Crank (Blue)"),
    1329: ("uIt0531", "Crank (Violet)"),
    1330: ("uIt0532", "Crank (Green)"),
    1537: ("", "Melee Vest"),
    1542: ("", "Bulletproof Vest"),
    1543: ("uIt0607", "Slate Map"),  # documents ?
    1544: ("uIt0608", "Combo Bonus"),  # documents ?
    1793: ("uIt0701", ""),  # documents ?
    1794: ("uIt0702", ""),  # documents ?
    1795: ("uIt0703", ""),  # documents ?
    1797: ("uIt0705", ""),  # documents ?
    1798: ("uIt0706", ""),  # documents ?
    1799: ("uIt0707", ""),  # documents ?
    1800: ("uIt0708", ""),  # documents ?
    1801: ("uIt0709", ""),  # documents ?
}


def item_class(item_id, default=None):
    """Returns mUnitClass for ItemId """
    item = ITEM_ID_TO_INFO.get(item_id)
    return item[0] if item and item[0] else default


def item_name(item_id, default=""):
    """Returns redable name if exists"""
    item = ITEM_ID_TO_INFO.get(item_id)
    return item[1] if item and item[1] else default


def item_ids_for(unit_class):
    """Returns all ItemId for the class(should be one)"""
    return [
        item_id for item_id, (mapped_class, _name) in ITEM_ID_TO_INFO.items()
        if mapped_class == unit_class
    ]


def enum_items():
    out = []
    for item_id, (unit_class, readable_name) in ITEM_ID_TO_INFO.items():
        if not unit_class:
            continue
        label = f"{item_id} — {unit_class}"
        if readable_name:
            label += f" ({readable_name})"
        out.append((str(item_id), label, ""))
    return out
