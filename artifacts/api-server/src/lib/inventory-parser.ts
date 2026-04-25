import nbt from "prismarine-nbt";

export interface ParsedItem {
  itemName: string;
  displayName: string;
  count: number;
  stackSize: number;
  container: string;
  isShulker: boolean;
}

const SHULKER_KEYWORDS = ["shulker_box", "shulker"];

function isShulker(name: string): boolean {
  return SHULKER_KEYWORDS.some((k) => name.includes(k));
}

function shulkerDisplayZh(name: string): string {
  const colorMap: Record<string, string> = {
    white: "白色",
    orange: "橙色",
    magenta: "品红",
    light_blue: "淡蓝",
    yellow: "黄色",
    lime: "黄绿",
    pink: "粉红",
    gray: "灰色",
    light_gray: "淡灰",
    cyan: "青色",
    purple: "紫色",
    blue: "蓝色",
    brown: "棕色",
    green: "绿色",
    red: "红色",
    black: "黑色",
  };
  for (const [k, v] of Object.entries(colorMap)) {
    if (name.startsWith(k + "_")) return `${v}潜影盒`;
  }
  return "潜影盒";
}

async function extractShulkerItems(
  itemNbt: any,
  mcData: any,
): Promise<Array<{ name: string; displayName: string; count: number; stackSize: number }>> {
  if (!itemNbt) return [];
  let parsed: any;
  try {
    if (itemNbt.value) {
      parsed = itemNbt;
    } else {
      parsed = (await nbt.parse(itemNbt)).parsed;
    }
  } catch {
    return [];
  }

  const blockEntityTag =
    parsed?.value?.BlockEntityTag?.value ||
    parsed?.value?.["minecraft:block_entity_data"]?.value ||
    parsed?.BlockEntityTag?.value;
  const itemsTag = blockEntityTag?.Items?.value?.value;
  if (!itemsTag || !Array.isArray(itemsTag)) return [];

  const out: Array<{ name: string; displayName: string; count: number; stackSize: number }> = [];
  for (const entry of itemsTag) {
    const idRaw =
      entry?.id?.value ||
      entry?.Item?.value?.id?.value ||
      entry?.id;
    const cntRaw =
      entry?.Count?.value ??
      entry?.count?.value ??
      entry?.Count ??
      entry?.count ??
      0;
    if (!idRaw) continue;
    const name = String(idRaw).replace(/^minecraft:/, "");
    const def = mcData.itemsByName?.[name];
    out.push({
      name,
      displayName: def?.displayName || name,
      count: Number(cntRaw) || 0,
      stackSize: def?.stackSize || 64,
    });
  }
  return out;
}

export async function parseSlotsToItems(
  slots: Array<any | null>,
  containerLabel: string,
  mcVersion: string,
): Promise<ParsedItem[]> {
  const mcData = (await import("minecraft-data")).default(mcVersion);
  const out: ParsedItem[] = [];

  for (let i = 0; i < slots.length; i++) {
    const slot = slots[i];
    if (!slot || !slot.name) continue;
    const def = mcData.itemsByName?.[slot.name];
    const stackSize = def?.stackSize || slot.stackSize || 64;

    out.push({
      itemName: slot.name,
      displayName: def?.displayName || slot.displayName || slot.name,
      count: slot.count,
      stackSize,
      container: containerLabel,
      isShulker: isShulker(slot.name),
    });

    if (isShulker(slot.name) && slot.nbt) {
      const inner = await extractShulkerItems(slot.nbt, mcData);
      const shulkerLabel = `${containerLabel} → ${shulkerDisplayZh(slot.name)}#${i}`;
      for (const it of inner) {
        out.push({
          itemName: it.name,
          displayName: it.displayName,
          count: it.count,
          stackSize: it.stackSize,
          container: shulkerLabel,
          isShulker: false,
        });
      }
    }
  }
  return out;
}
