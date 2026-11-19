"""RE5 item IDs: ``mItemSet.ItemId`` -> (unit class, readable name, type)
    item id is use in lot files with the uinit class name
"""

ITEM_ID_RE5 = {
    256: ("uWp00", "Hand-to-Hand", "weapon special"),
    257: ("uWp01", "Knife", "weapon special"),
    258: ("uWp02", "M92F", "weapon"),
    259: ("uWp03", "VZ61", "weapon"),
    260: ("uWp04", "Ithaca M37", "weapon"),
    261: ("uWp05", "S75", "weapon"),
    262: ("uWp06", "Hand Grenade", "weapon"),
    263: ("uWp07", "Incendiary Grenade", "weapon"),
    264: ("uWp08", "Flash Grenade", "weapon"),
    265: ("uWp09", "SIG 556", "weapon"),
    266: ("uWp0a", "Proximity Mines", "weapon"),
    267: ("uWp0b", "S&W M29", "weapon"),
    268: ("uWp0c", "Grenade Launcher", "weapon"),
    269: ("uWp0d", "Rocket Launcher", "weapon"),
    270: ("uWp0e", "Knife", "weapon special"),
    271: ("uWp0f", "Longbow", "weapon"),
    272: ("uWp10", "H&K P8", "weapon"),
    273: ("uWp11", "SIG P226", "weapon"),
    274: ("uWp12", "Samurai Edge", "weapon"),
    275: ("uWp13", "H&K MP5", "weapon"),
    276: ("uWp14", "Dummy", "weapon special"),  # knife that can be used as an equipable weapon, no icon
    277: ("uWp15", "Gatling Gun", "weapon"),
    278: ("uWp16", "M3", "weapon"),
    279: ("uWp17", "Jail Breaker", "weapon"),
    281: ("uWp19", "Hydra", "weapon"),
    282: ("uWp1a", "L. Hawk", "weapon"),
    283: ("uWp1b", "S&W M500", "weapon"),
    284: ("uWp1c", "H&K PSG-1", "weapon"),
    285: ("uWp1d", "AK-74", "weapon"),
    286: ("uWp1e", "M93R", "weapon"),
    287: ("uWp1f", "Px4", "weapon"),
    288: ("uWp20", "Dragunov SVD", "weapon"),
    289: ("uWp21", "Flamethrower", "weapon"),
    290: ("uWp22", "Stun Rod", "weapon"),
    293: ("uWp25", "G. Launcher (EXP)", "weapon"),  # grenade launcher with explosive rounds
    294: ("uWp26", "G. Launcher (ACD)", "weapon"),  # grenade launcher with acid rounds
    295: ("uWp27", "G. Launcher (ICE)", "weapon"),  # grenade launcher with nitrogen rounds
    297: ("uWp29", "Samurai Edge", "weapon"),
    298: ("", "Unused item ID (no class)", ""),
    300: ("uWp2c", "Irving's Boat Gun", "weapon special"),
    303: ("uWp2f", "Gun Turret", "weapon special"),
    304: ("uWp30", "Lantern", "weapon special"),
    308: ("uWp34", "L.T.D.", "weapon special"),
    309: ("uWp35", "Rocket Launcher (NVS)", "weapon special"),
    310: ("uWp36", "Egg (Rotten)", "weapon"),
    313: ("uWp39", "G. Launcher (FLM)", "weapon"),  # grenade launcher with flame rounds
    314: ("uWp3a", "G. Launcher (FLS)", "weapon"),  # grenade launcher with flash rounds
    315: ("uWp3b", "G. Launcher (ELC)", "weapon"),  # grenade launcher with electric rounds
    316: ("uWp3c", "Egg (White)", "item"),
    317: ("uWp3d", "Egg (Brown)", "item"),
    318: ("uWp3e", "Egg (Gold)", "item"),
    336: ("uWp50", "Adze", "weapon npc"),
    337: ("uWp51", "Sickle", "weapon npc"),
    338: ("uWp52", "Bow Gun", "weapon npc"),
    339: ("uWp53", "Shovel", "weapon npc"),
    340: ("uWp54", "Dynamite", "weapon npc"),
    341: ("uWp55", "Machete", "weapon npc"),
    344: ("uWp58", "Giant Axe", "weapon npc"),
    345: ("uWp59", "Steel Pipe", "weapon npc"),
    346: ("uWp5a", "Bottle", "weapon npc"),
    347: ("uWp5b", "Chainsaw", "weapon npc"),
    349: ("uWp5d", "Gatling Gun", "weapon npc"),
    350: ("uWp5e", "Torch", "weapon npc"),
    351: ("uWp5f", "Spear", "weapon npc"),
    352: ("uWp60", "Shield", "weapon npc"),
    354: ("uWp62", "Bow", "weapon npc"),
    356: ("uWp64", "Morning Star", "weapon npc"),
    357: ("uWp65", "Stun Rod", "weapon npc"),
    377: ("uWp79", "Electric Post (Golem)", "weapon npc"),
    513: ("uIt0201", "Handgun Ammo", "ammo"),
    514: ("uIt0202", "Machine Gun Ammo", "ammo"),
    515: ("uIt0203", "Shotgun Ammo", "ammo"),
    516: ("uIt0204", "Rifle Ammo", "ammo"),
    518: ("uIt0206", "Explosive Rounds", "ammo"),
    519: ("uIt0207", "Acid Rounds", "ammo"),
    520: ("uIt0208", "Nitrogen Rounds", "ammo"),
    521: ("uIt0209", "Magnum Ammo", "ammo"),
    526: ("uIt020e", "Flame Rounds", "ammo"),
    527: ("uIt020f", "Flash Rounds", "ammo"),
    528: ("uIt0210", "Electric Rounds", "ammo"),
    529: ("uIt0211", "RPG Round", "ammo"),
    769: ("uIt0301", "Herb (Green)", "item"),
    770: ("uIt0302", "Herb (Red)", "item"),
    771: ("", "Herb (X)", ""),
    772: ("uIt0304", "First Aid Spray", "item"),
    773: ("uIt0305", "Herb (Green)", "item"),
    774: ("uIt0306", "Herb (Red)", "item"),
    775: ("uIt0307", "Herb (G+G)", "item"),
    776: ("", "Herb (G+G+G)", ""),
    777: ("uIt0309", "Herb (G+R)", "item"),
    778: ("", "Herb (G+X)", ""),
    779: ("", "Herb (G+R+X)", ""),
    780: ("", "Egg (White)", ""),
    781: ("", "Egg (Brown)", ""),
    782: ("", "Egg (Gold)", ""),
    783: ("", "Nile Perch", ""),
    784: ("", "Nile Perch (Big)", ""),
    785: ("", "Water", ""),
    786: ("", "Herb (X)", ""),
    1025: ("uIt0401", "Gold (Large)", "treasure"),
    1026: ("uIt0402", "Gold (Small)", "treasure"),
    1027: ("uIt0403", "Gold Bars", "treasure"),
    1028: ("", "Sapphire", ""),
    1047: ("uIt0417", "Gold Ring", ""),
    1048: ("uIt0418", "Dead Bride's Necklace", "treasure"),
    1049: ("uIt0419", "Venom Fang", "treasure"),
    1050: ("uIt041a", "Antique Clock", "treasure"),
    1051: ("uIt041b", "Chalice (Silver)", "treasure"),
    1052: ("uIt041c", "Chalice (Gold)", "treasure"),
    1053: ("uIt041d", "Idol (Silver)", "treasure"),
    1054: ("uIt041e", "Idol (Gold)", "treasure"),
    1055: ("uIt041f", "Ceremonial Mask", "treasure"),
    1056: ("uIt0420", "Ivory Relief", "treasure"),
    1057: ("uIt0421", "Beetle (Brown)", "treasure"),
    1058: ("uIt0422", "Jewel Beetle", "treasure"),
    1059: ("uIt0423", "Royal Necklace", "treasure"),
    1060: ("uIt0424", "Jewel Bangle", "treasure"),
    1061: ("uIt0425", "Beetle (Gold)", "treasure"),
    1062: ("uIt0426", "Beetle (Emerald Green)", "treasure"),
    1063: ("uIt0427", "Score Star (Small)", "treasure"),
    1064: ("uIt0428", "Score Star (Medium)", "treasure"),
    1065: ("uIt0429", "Score Star (Large)", "treasure"),
    1104: ("uIt0450", "Topaz (Pear)", "treasure"),
    1105: ("uIt0451", "Ruby (Pear)", "treasure"),
    1106: ("uIt0452", "Sapphire (Pear)", "treasure"),
    1107: ("uIt0453", "Emerald (Pear)", "treasure"),
    1108: ("uIt0454", "Diamond (Pear)", "treasure"),
    1111: ("uIt0457", "Topaz (Square)", "treasure"),
    1112: ("uIt0458", "Ruby (Square)", "treasure"),
    1113: ("uIt0459", "Sapphire (Square)", "treasure"),
    1114: ("uIt045a", "Emerald (Square)", "treasure"),
    1115: ("uIt045b", "Diamond (Square)", "treasure"),
    1118: ("uIt045e", "Topaz (Oval)", "treasure"),
    1119: ("uIt045f", "Ruby (Oval)", "treasure"),
    1120: ("uIt0460", "Sapphire (Oval)", "treasure"),
    1121: ("uIt0461", "Emerald (Oval)", "treasure"),
    1122: ("uIt0462", "Diamond (Oval)", "treasure"),
    1125: ("uIt0465", "Topaz (Trilliant)", "treasure"),
    1126: ("uIt0466", "Ruby (Trilliant)", "treasure"),
    1127: ("uIt0467", "Sapphire (Trilliant)", "treasure"),
    1128: ("uIt0468", "Emerald (Trilliant)", "treasure"),
    1129: ("uIt0469", "Diamond (Trilliant)", "treasure"),
    1132: ("uIt046c", "Power Stone", "treasure"),
    1133: ("uIt046d", "Lion Heart", "treasure"),
    1134: ("uIt046e", "Blue Enigma", "treasure"),
    1135: ("uIt046f", "Soul Gem", "treasure"),
    1136: ("uIt0470", "Heart of Africa", "treasure"),
    1139: ("uIt0473", "Topaz (Marquise)", "treasure"),
    1140: ("uIt0474", "Ruby (Marquise)", "treasure"),
    1141: ("uIt0475", "Sapphire (Marquise)", "treasure"),
    1142: ("uIt0476", "Emerald (Marquise)", "treasure"),
    1143: ("uIt0477", "Diamond (Marquise)", "treasure"),
    1146: ("uIt047a", "Topaz (Brilliant)", "treasure"),
    1147: ("uIt047b", "Ruby (Brilliant)", "treasure"),
    1148: ("uIt047c", "Sapphire (Brilliant)", "treasure"),
    1149: ("uIt047d", "Emerald (Brilliant)", "treasure"),
    1150: ("uIt047e", "Diamond (Brilliant)", "treasure"),
    1281: ("", "Punisher's Key", ""),
    1282: ("", "Punisher's Key", ""),
    1283: ("uIt0503", "Furnace Key", "item quest"),
    1285: ("", "Execution Ground Key", ""),
    1286: ("uIt0506", "Port Key", "item quest"),
    1287: ("uIt0507", "Hangar Keycard A", "item quest"),
    1288: ("uIt0508", "Hangar Keycard B", "item quest"),
    1289: ("uIt0509", "Old Building Key", "item quest"),
    1290: ("uIt050A", "Tanker Keycard A", "item quest"),
    1294: ("uIt050E", "Sky Emblem", "item quest"),
    1295: ("uIt050F", "Earth Emblem", "item quest"),
    1296: ("uIt0510", "Sea Emblem", "item quest"),
    1298: ("uIt0512", "Shaman Slate", "item quest"),
    1299: ("uIt0513", "Warrior Slate", "item quest"),
    1300: ("uIt0514", "Beast Slate", "item quest"),
    1301: ("uIt0515", "Raptor Slate", "item quest"),
    1302: ("uIt0516", "Crane Keycard", "item quest"),
    1303: ("uIt0517", "Tanker Keycard B", "item quest"),
    1304: ("", "Warrior Slate", ""),
    1306: ("uIt051A", "Guard's Key", "item quest"),
    1307: ("uIt051B", "Bridge Keycard", "item quest"),
    1312: ("uIt0520", "Square Crank", "item quest"),
    1313: ("uIt0521", "Centaur Emblem", "item quest"),
    1314: ("uIt0522", "Password 1", "item quest"),
    1315: ("uIt0523", "Password 2", "item quest"),
    1316: ("uIt0524", "Password 3", "item quest"),
    1317: ("uIt0525", "Jail Key", "item quest"),
    1318: ("uIt0526", "Gold Crest", "item quest"),
    1319: ("uIt0527", "Silver Crest", "item quest"),
    1320: ("uIt0528", "Heat-Sensitive Paper", "item quest"),
    1321: ("uIt0529", "Transport Area Key", "item quest"),
    1322: ("uIt052A", "Emergency Exit Key", "item quest"),
    1323: ("uIt052B", "Sun Eater Serpent Shard", "item quest"),
    1324: ("uIt052C", "Dual-Head Serpent Shard", "item quest"),
    1325: ("uIt052D", "Serpent Tail Shard", "item quest"),
    1326: ("uIt052E", "Tri-Head Serpent Shard", "item quest"),
    1327: ("uIt052F", "Crank (Red)", "item quest"),
    1328: ("uIt0530", "Crank (Blue)", "item quest"),
    1329: ("uIt0531", "Crank (Violet)", "item quest"),
    1330: ("uIt0532", "Crank (Green)", "item quest"),
    1537: ("uIt0601", "Melee Vest", "armor"),
    1542: ("uIt0606", "Bulletproof Vest", "armor"),
    1543: ("uIt0607", "Slate Map", "treasure"),
    1544: ("uIt0608", "Combo Bonus", "mercenaries"),
    1793: ("uIt0701", "", "item dummy"),  # objects that trigger reading some text
    1794: ("uIt0702", "", "item dummy"),
    1795: ("uIt0703", "", "item dummy"),
    1796: ("uIt0704", "", "item dummy"),
    1797: ("uIt0705", "", "item dummy"),
    1798: ("uIt0706", "", "item dummy"),
    1799: ("uIt0707", "", "item dummy"),
    1800: ("uIt0708", "", "item dummy"),
    1801: ("uIt0709", "", "item dummy"),
}


def get_item_class(item_id, default=None):
    """Returns mUnitClass for ItemId """
    item = ITEM_ID_RE5.get(item_id)
    return item[0] if item and item[0] else default


def get_item_name(item_id, default=""):
    """Returns redable name if exists"""
    item = ITEM_ID_RE5.get(item_id)
    return item[1] if item and item[1] else default


def get_item_type(item_id, default=""):
    """Returns the category assigned to an ItemId."""
    item = ITEM_ID_RE5.get(item_id)
    return item[2] if item and item[2] else default


def get_item_ids_for(unit_class):
    """Returns all ItemId for the class(should be one)"""
    return [
        item_id for item_id, (mapped_class, _name, _type) in ITEM_ID_RE5.items()
        if mapped_class == unit_class
    ]


def get_item_types():
    """Returns categories that have at least one mapped unit class."""
    item_types = []
    for unit_class, _item_name, item_type in ITEM_ID_RE5.values():
        if unit_class and item_type not in item_types:
            item_types.append(item_type)
    return item_types


def enum_items(item_type=None):
    """Builds Blender enum entries, optionally filtered by item category."""
    out = []
    for item_id, (unit_class, item_name, mapped_type) in ITEM_ID_RE5.items():
        if not unit_class:
            continue
        if item_type is not None and mapped_type != item_type:
            continue
        label = f"{item_id} — {unit_class}"
        if item_name:
            label += f" ({item_name})"
        out.append((str(item_id), label, ""))
    return out
