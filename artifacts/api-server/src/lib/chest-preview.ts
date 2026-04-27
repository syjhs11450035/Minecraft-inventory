// 箱子預覽：透過 mineflayer 直接查詢 server 端的箱子內容，
// 而不需要把機器人實體走過去「打開」。
//
// 主要策略：
// 1. 用 `/data get block X Y Z Items` 取得 SNBT 字串並解析（需 OP）
// 2. 若失敗（沒 OP / 不是該維度），fallback 用 bot.openContainer() 並
//    立即關閉（不寫入 DB）。

import { getBot, findNearbyChest } from "./bot";
import { parseSlotsToItems, type ParsedItem } from "./inventory-parser";
import { logEvent } from "./event-log";

export interface ChestPreviewResult {
  via: "data-get" | "open-container";
  target: { x: number; y: number; z: number; name: string };
  items: ParsedItem[];
}

/** 從 `/data get block` 的回應中抽出 Items 陣列字串。 */
function extractItemsBlock(response: string): string | null {
  const idx = response.search(/Items\s*:\s*\[/i);
  if (idx < 0) return null;
  const open = response.indexOf("[", idx);
  if (open < 0) return null;
  let depth = 0;
  for (let i = open; i < response.length; i++) {
    const ch = response[i];
    if (ch === "[") depth++;
    else if (ch === "]") {
      depth--;
      if (depth === 0) return response.slice(open + 1, i);
    }
  }
  return null;
}

/** 把 SNBT 物品段落（例如 `{Slot:0b,id:"minecraft:dirt",Count:64b}`）解析成普通物件。 */
function parseSnbtItems(inner: string): Array<Record<string, any>> {
  const items: Array<Record<string, any>> = [];
  let depth = 0;
  let start = -1;
  let inStr = false;
  let escape = false;
  for (let i = 0; i < inner.length; i++) {
    const ch = inner[i];
    if (escape) {
      escape = false;
      continue;
    }
    if (ch === "\\") {
      escape = true;
      continue;
    }
    if (ch === '"') inStr = !inStr;
    if (inStr) continue;
    if (ch === "{") {
      if (depth === 0) start = i + 1;
      depth++;
    } else if (ch === "}") {
      depth--;
      if (depth === 0 && start >= 0) {
        const obj = parseSnbtObject(inner.slice(start, i));
        if (obj) items.push(obj);
        start = -1;
      }
    }
  }
  return items;
}

function parseSnbtObject(body: string): Record<string, any> | null {
  const obj: Record<string, any> = {};
  const pairs = splitTopLevel(body, ",");
  for (const pair of pairs) {
    const eq = pair.indexOf(":");
    if (eq < 0) continue;
    const key = pair.slice(0, eq).trim();
    const valRaw = pair.slice(eq + 1).trim();
    obj[key] = parseSnbtValue(valRaw);
  }
  return obj;
}

function splitTopLevel(s: string, sep: string): string[] {
  const out: string[] = [];
  let depth = 0;
  let inStr = false;
  let escape = false;
  let last = 0;
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (escape) {
      escape = false;
      continue;
    }
    if (ch === "\\") {
      escape = true;
      continue;
    }
    if (ch === '"') inStr = !inStr;
    if (inStr) continue;
    if (ch === "{" || ch === "[") depth++;
    else if (ch === "}" || ch === "]") depth--;
    else if (ch === sep && depth === 0) {
      out.push(s.slice(last, i));
      last = i + 1;
    }
  }
  out.push(s.slice(last));
  return out.map((x) => x.trim()).filter(Boolean);
}

function parseSnbtValue(v: string): any {
  if (!v) return null;
  if (v.startsWith('"')) {
    return v.slice(1, -1).replace(/\\(.)/g, "$1");
  }
  // 1.20.5+ 用 'minecraft:dirt' 也常見
  if (v.startsWith("'")) {
    return v.slice(1, -1);
  }
  if (v.startsWith("{")) {
    return parseSnbtObject(v.slice(1, -1));
  }
  if (v.startsWith("[")) {
    const inner = v.slice(1, -1);
    if (/^\s*[BIL];/.test(inner)) {
      return inner
        .replace(/^\s*[BIL];\s*/, "")
        .split(",")
        .map((x) => Number(x.replace(/[bsLfd]$/i, "")));
    }
    return splitTopLevel(inner, ",").map(parseSnbtValue);
  }
  // 數字（可能後綴 b/s/L/f/d）
  const m = v.match(/^(-?\d+\.?\d*)[bsLfdBSLFD]?$/);
  if (m) return Number(m[1]);
  if (v === "true") return true;
  if (v === "false") return false;
  return v;
}

interface FlexibleItem {
  Slot?: number;
  slot?: number;
  id?: string;
  Count?: number;
  count?: number;
}

function snbtItemsToSlotArray(parsed: FlexibleItem[], totalSlots = 54): Array<any | null> {
  const slots: Array<any | null> = new Array(totalSlots).fill(null);
  for (const it of parsed) {
    const slot = it.Slot ?? it.slot;
    const id = String(it.id ?? "").replace(/^minecraft:/, "");
    const count = Number(it.Count ?? it.count ?? 0);
    if (typeof slot !== "number" || !id || count <= 0) continue;
    if (slot >= 0 && slot < totalSlots) {
      slots[slot] = {
        name: id,
        type: -1,
        count,
        nbt: null,
      };
    }
  }
  return slots;
}

async function tryDataGet(target: {
  x: number;
  y: number;
  z: number;
}): Promise<Array<any | null> | null> {
  const bot = getBot();
  if (!bot) return null;

  return new Promise((resolve) => {
    let done = false;
    const finish = (v: Array<any | null> | null) => {
      if (done) return;
      done = true;
      bot.removeListener("messagestr", onMsg);
      resolve(v);
    };

    const onMsg = (text: string) => {
      const s = String(text || "");
      if (
        /^\s*Block has the following block data/i.test(s) ||
        /Block has the following block data/i.test(s)
      ) {
        const inner = extractItemsBlock(s);
        if (inner !== null) {
          const parsed = parseSnbtItems(inner) as FlexibleItem[];
          finish(snbtItemsToSlotArray(parsed));
          return;
        }
      }
      if (/Found no elements/i.test(s) || /No element of type/i.test(s)) {
        // 空箱
        finish(snbtItemsToSlotArray([]));
        return;
      }
      if (/Unknown or incomplete command|incorrect argument|permission/i.test(s)) {
        finish(null);
      }
    };

    bot.on("messagestr", onMsg);

    try {
      bot.chat(`/data get block ${target.x} ${target.y} ${target.z} Items`);
    } catch {
      finish(null);
      return;
    }

    setTimeout(() => finish(null), 1500);
  });
}

async function fallbackOpen(range: number): Promise<{
  target: { x: number; y: number; z: number; name: string };
  slots: Array<any | null>;
} | null> {
  const bot = getBot();
  if (!bot) return null;
  const target = await findNearbyChest(range);
  if (!target) return null;
  const Vec3 = bot.entity.position.constructor;
  const block = bot.blockAt(new Vec3(target.x, target.y, target.z));
  if (!block) return null;
  const container = await bot.openContainer(block);
  await new Promise((r) => setTimeout(r, 200));
  const slots = (container.slots as Array<any | null>).slice(
    0,
    container.inventoryStart ?? container.slots.length,
  );
  try {
    container.close();
  } catch {
    // ignore
  }
  return { target, slots };
}

export async function previewChest(opts: {
  x?: number | null;
  y?: number | null;
  z?: number | null;
  range?: number;
}): Promise<ChestPreviewResult> {
  const bot = getBot();
  if (!bot) throw new Error("机器人未上线");

  let target: { x: number; y: number; z: number; name: string } | null;
  if (
    typeof opts.x === "number" &&
    typeof opts.y === "number" &&
    typeof opts.z === "number"
  ) {
    target = { x: opts.x, y: opts.y, z: opts.z, name: "Container" };
  } else {
    const range = Math.min(32, Math.max(1, Number(opts.range ?? 6) || 6));
    target = await findNearbyChest(range);
    if (!target) throw new Error(`附近 ${range} 格内找不到箱子/木桶/末影箱`);
  }

  // 嘗試用 /data get
  const slotsFromData = await tryDataGet(target);
  if (slotsFromData) {
    const items = await parseSlotsToItems(slotsFromData, target.name, bot.version);
    logEvent("info", `🔍 預覽箱子 (${target.x},${target.y},${target.z})：${items.length} 笔（/data get）`);
    return { via: "data-get", target, items };
  }

  // fallback：開箱-關閉，不入庫
  const range = Math.min(32, Math.max(1, Number(opts.range ?? 6) || 6));
  const opened = await fallbackOpen(range);
  if (!opened) throw new Error("无法预览此箱子（请确认机器人有 OP 或可走到附近）");
  const items = await parseSlotsToItems(opened.slots, opened.target.name, bot.version);
  logEvent(
    "info",
    `🔍 預覽箱子 (${opened.target.x},${opened.target.y},${opened.target.z})：${items.length} 笔（fallback）`,
  );
  return { via: "open-container", target: opened.target, items };
}
