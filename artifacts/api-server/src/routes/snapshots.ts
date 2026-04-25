import { Router, type IRouter } from "express";
import { db, containerSnapshots, snapshotItems } from "@workspace/db";
import { eq, desc, sql } from "drizzle-orm";
import { getBot, getBotState, openNearbyChest } from "../lib/bot";
import { parseSlotsToItems } from "../lib/inventory-parser";
import { logEvent } from "../lib/event-log";

const router: IRouter = Router();

router.post("/snapshots/inventory", async (req, res) => {
  const bot = getBot();
  if (!bot) {
    res.status(400).json({ error: "机器人未上线" });
    return;
  }
  const label = String(req.body?.label ?? "机器人主背包");
  const state = getBotState();

  try {
    const slots = bot.inventory.slots as Array<any | null>;
    const items = await parseSlotsToItems(slots, "主背包", bot.version);

    const [snap] = await db
      .insert(containerSnapshots)
      .values({
        sourceType: "inventory",
        sourceKey: "inventory",
        label,
        dimension: state.position?.dimension ?? null,
        x: state.position?.x ?? null,
        y: state.position?.y ?? null,
        z: state.position?.z ?? null,
      })
      .returning();

    if (items.length > 0) {
      await db.insert(snapshotItems).values(
        items.map((it) => ({
          snapshotId: snap.id,
          itemName: it.itemName,
          displayName: it.displayName,
          count: it.count,
          stackSize: it.stackSize,
          container: it.container,
          isShulker: it.isShulker,
        })),
      );
    }

    logEvent("info", `背包快照 #${snap.id} 已建立（${items.length} 笔物品）`);
    res.json({ ok: true, snapshot: snap, itemCount: items.length });
  } catch (err: any) {
    logEvent("error", `背包快照失败：${err.message}`);
    res.status(500).json({ error: err.message });
  }
});

router.post("/snapshots/chest", async (req, res) => {
  const bot = getBot();
  if (!bot) {
    res.status(400).json({ error: "机器人未上线" });
    return;
  }
  const label =
    String(req.body?.label ?? "").trim() || "未命名容器";
  const range = Math.min(
    32,
    Math.max(1, Number(req.body?.range ?? 6) || 6),
  );
  const state = getBotState();

  let opened: any = null;
  try {
    const result = await openNearbyChest(range);
    opened = result.container;
    const target = result.target;

    // Wait one tick for slots to populate
    await new Promise((r) => setTimeout(r, 200));

    const slots = (opened.slots as Array<any | null>).slice(
      0,
      opened.inventoryStart ?? opened.slots.length,
    );

    const items = await parseSlotsToItems(slots, target.name, bot.version);

    const [snap] = await db
      .insert(containerSnapshots)
      .values({
        sourceType: "chest",
        sourceKey: `${state.position?.dimension ?? "?"}:${target.x},${target.y},${target.z}`,
        label,
        dimension: state.position?.dimension ?? null,
        x: target.x,
        y: target.y,
        z: target.z,
        notes: target.name,
      })
      .returning();

    if (items.length > 0) {
      await db.insert(snapshotItems).values(
        items.map((it) => ({
          snapshotId: snap.id,
          itemName: it.itemName,
          displayName: it.displayName,
          count: it.count,
          stackSize: it.stackSize,
          container: it.container,
          isShulker: it.isShulker,
        })),
      );
    }

    logEvent(
      "info",
      `容器快照 #${snap.id}：${target.name} @ (${target.x},${target.y},${target.z}) — ${items.length} 笔物品`,
    );
    res.json({
      ok: true,
      snapshot: snap,
      target,
      itemCount: items.length,
    });
  } catch (err: any) {
    logEvent("error", `开启箱子失败：${err.message}`);
    res.status(500).json({ error: err.message });
  } finally {
    try {
      opened?.close?.();
    } catch {
      // ignore
    }
  }
});

router.get("/snapshots", async (_req, res) => {
  const rows = await db
    .select()
    .from(containerSnapshots)
    .orderBy(desc(containerSnapshots.takenAt))
    .limit(200);
  res.json({ snapshots: rows });
});

router.get("/snapshots/:id", async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id)) {
    res.status(400).json({ error: "无效 ID" });
    return;
  }
  const [snap] = await db
    .select()
    .from(containerSnapshots)
    .where(eq(containerSnapshots.id, id));
  if (!snap) {
    res.status(404).json({ error: "找不到此快照" });
    return;
  }
  const items = await db
    .select()
    .from(snapshotItems)
    .where(eq(snapshotItems.snapshotId, id));
  res.json({ snapshot: snap, items });
});

router.delete("/snapshots/:id", async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id)) {
    res.status(400).json({ error: "无效 ID" });
    return;
  }
  await db.delete(containerSnapshots).where(eq(containerSnapshots.id, id));
  logEvent("system", `已删除快照 #${id}`);
  res.json({ ok: true });
});

router.get("/inventory/aggregate", async (_req, res) => {
  // Aggregate the latest snapshot per source_key, only counting top-level items
  // (skip shulker_box items so we don't double-count their inner contents)
  const rows = await db.execute(sql`
    WITH latest AS (
      SELECT DISTINCT ON (source_key) id, source_key, label, taken_at
      FROM container_snapshots
      ORDER BY source_key, taken_at DESC
    ),
    items AS (
      SELECT si.item_name, si.display_name, si.count, si.stack_size, si.is_shulker, si.container, l.label as source_label
      FROM snapshot_items si
      JOIN latest l ON si.snapshot_id = l.id
      WHERE si.is_shulker = false
    )
    SELECT
      item_name,
      MAX(display_name) AS display_name,
      MAX(stack_size) AS stack_size,
      SUM(count)::int AS total
    FROM items
    GROUP BY item_name
    ORDER BY total DESC
  `);

  const items = (rows.rows as any[]).map((r) => {
    const stack = Number(r.stack_size) || 64;
    const total = Number(r.total) || 0;
    const perBox = stack * 27;
    const boxes = Math.floor(total / perBox);
    const rem = total - boxes * perBox;
    const stacks = Math.floor(rem / stack);
    const singles = rem - stacks * stack;
    return {
      itemName: r.item_name,
      displayName: r.display_name,
      stackSize: stack,
      total,
      boxes,
      stacks,
      singles,
    };
  });

  res.json({ items });
});

export default router;
