"""物品 emoji 图标对照表与查找函式。"""

from __future__ import annotations

ITEM_ICONS: dict[str, str] = {
    "diamond": "💎", "diamond_block": "💎", "diamond_ore": "💎",
    "iron_ingot": "🥈", "iron_block": "🥈", "iron_ore": "🥈", "raw_iron": "🪨",
    "gold_ingot": "🥇", "gold_block": "🥇", "gold_ore": "🥇", "raw_gold": "🪨",
    "emerald": "💚", "emerald_block": "💚", "emerald_ore": "💚",
    "redstone": "🔴", "redstone_block": "🔴", "redstone_ore": "🔴",
    "coal": "⚫", "coal_block": "⚫", "coal_ore": "⚫", "charcoal": "⚫",
    "lapis_lazuli": "🔵", "lapis_block": "🔵", "lapis_ore": "🔵",
    "netherite_ingot": "🟪", "netherite_block": "🟪", "ancient_debris": "🟪",
    "stone": "🧱", "cobblestone": "🪨", "deepslate": "🪨", "cobbled_deepslate": "🪨",
    "dirt": "🟫", "grass_block": "🌱", "podzol": "🟫", "mycelium": "🟪",
    "sand": "⏳", "red_sand": "🟧", "gravel": "⚪",
    "oak_log": "🪵", "spruce_log": "🪵", "birch_log": "🪵",
    "jungle_log": "🪵", "acacia_log": "🪵", "dark_oak_log": "🪵",
    "mangrove_log": "🪵", "cherry_log": "🌸", "bamboo_block": "🎋",
    "oak_planks": "🟫", "spruce_planks": "🟫", "birch_planks": "🟫",
    "water_bucket": "💧", "lava_bucket": "🔥", "milk_bucket": "🥛", "bucket": "🪣",
    "bread": "🍞", "cooked_beef": "🥩", "cooked_porkchop": "🥓",
    "cooked_chicken": "🍗", "cooked_mutton": "🍖", "cooked_salmon": "🐟",
    "apple": "🍎", "golden_apple": "🍏", "enchanted_golden_apple": "🍏",
    "carrot": "🥕", "potato": "🥔", "baked_potato": "🥔",
    "wheat": "🌾", "wheat_seeds": "🌱", "sugar_cane": "🎋", "melon_slice": "🍉",
    "pumpkin": "🎃", "cake": "🍰", "cookie": "🍪",
    "diamond_sword": "⚔️", "iron_sword": "⚔️", "stone_sword": "⚔️",
    "wooden_sword": "⚔️", "golden_sword": "⚔️", "netherite_sword": "⚔️",
    "diamond_pickaxe": "⛏️", "iron_pickaxe": "⛏️", "stone_pickaxe": "⛏️",
    "wooden_pickaxe": "⛏️", "golden_pickaxe": "⛏️", "netherite_pickaxe": "⛏️",
    "diamond_axe": "🪓", "iron_axe": "🪓", "stone_axe": "🪓",
    "wooden_axe": "🪓", "golden_axe": "🪓", "netherite_axe": "🪓",
    "bow": "🏹", "crossbow": "🏹", "arrow": "➡️", "spectral_arrow": "✨",
    "shield": "🛡️", "totem_of_undying": "🌟",
    "ender_pearl": "🟣", "ender_eye": "👁️", "ender_chest": "📦",
    "experience_bottle": "🧪", "potion": "🧪", "splash_potion": "🧪",
    "tnt": "💣", "fire_charge": "🔥", "flint_and_steel": "🔥",
    "torch": "🔦", "lantern": "🏮", "soul_torch": "🔵",
    "chest": "📦", "trapped_chest": "📦", "barrel": "🛢️", "shulker_box": "📦",
    "elytra": "🪽", "trident": "🔱", "nautilus_shell": "🐚",
    "name_tag": "🏷️", "lead": "🪢", "compass": "🧭", "clock": "🕐",
    "map": "🗺️", "filled_map": "🗺️",
    "book": "📕", "written_book": "📖", "writable_book": "📓",
    "enchanted_book": "✨", "bookshelf": "📚",
    "music_disc_13": "💿", "jukebox": "🎵",
    "spawner": "🥚", "beacon": "💡", "conduit": "💡",
    "blaze_rod": "🔥", "blaze_powder": "🟡", "ghast_tear": "💧",
    "nether_star": "⭐", "dragon_egg": "🥚", "dragon_breath": "🌬️",
    "egg": "🥚", "snowball": "❄️", "ice": "🧊", "packed_ice": "🧊",
    "obsidian": "🟪", "crying_obsidian": "🟪", "bedrock": "⬛",
    "string": "🧵", "feather": "🪶", "leather": "🟫",
    "iron_nugget": "🔘", "gold_nugget": "🔘",
    "saddle": "🐎", "carrot_on_a_stick": "🥕",
    "fishing_rod": "🎣", "cod": "🐟", "salmon": "🐟",
}

DEFAULT_ICON = "🔹"


def icon_for(item_name: str) -> str:
    if item_name in ITEM_ICONS:
        return ITEM_ICONS[item_name]
    if "shulker_box" in item_name:
        return "📦"
    if "_log" in item_name or "_planks" in item_name:
        return "🪵"
    if "_ore" in item_name:
        return "🪨"
    if "_sword" in item_name:
        return "⚔️"
    if "_pickaxe" in item_name:
        return "⛏️"
    if "_axe" in item_name:
        return "🪓"
    if (
        "_helmet" in item_name
        or "_chestplate" in item_name
        or "_leggings" in item_name
        or "_boots" in item_name
    ):
        return "🛡️"
    return DEFAULT_ICON
