import { Router, type IRouter } from "express";
import { db, chestAreas, containerSnapshots } from "@workspace/db";
import { eq, sql, asc } from "drizzle-orm";
import { z } from "zod/v4";
import { logEvent } from "../lib/event-log";

const router: IRouter = Router();

const AreaSchema = z.object({
  name: z.string().min(1).max(80),
  description: z.string().max(300).optional().nullable(),
  color: z.string().max(20).optional().nullable(),
  vertex1: z.string().max(60).optional().nullable(),
  vertex2: z.string().max(60).optional().nullable(),
  extendsFrom: z.string().max(80).optional().nullable(),
});

router.get("/areas", async (_req, res) => {
  const rows = await db.execute(sql`
    SELECT
      a.id,
      a.name,
      a.description,
      a.color,
      a.vertex1,
      a.vertex2,
      a.extends_from,
      a.created_at,
      COUNT(s.id)::int AS snapshot_count
    FROM chest_areas a
    LEFT JOIN container_snapshots s ON s.area_id = a.id
    GROUP BY a.id
    ORDER BY a.created_at ASC
  `);
  res.json({
    areas: (rows.rows as any[]).map((r) => ({
      id: r.id,
      name: r.name,
      description: r.description,
      color: r.color,
      vertex1: r.vertex1,
      vertex2: r.vertex2,
      extendsFrom: r.extends_from,
      createdAt: r.created_at,
      snapshotCount: Number(r.snapshot_count) || 0,
    })),
  });
});

router.post("/areas", async (req, res) => {
  const parsed = AreaSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "参数错误", details: parsed.error.message });
    return;
  }
  const [row] = await db
    .insert(chestAreas)
    .values({
      name: parsed.data.name,
      description: parsed.data.description ?? null,
      color: parsed.data.color ?? null,
      vertex1: parsed.data.vertex1 ?? null,
      vertex2: parsed.data.vertex2 ?? null,
      extendsFrom: parsed.data.extendsFrom ?? null,
    })
    .returning();
  logEvent("system", `新增区域：${row.name} (#${row.id})`);
  res.json({ ok: true, area: row });
});

router.patch("/areas/:id", async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id)) {
    res.status(400).json({ error: "无效 ID" });
    return;
  }
  const parsed = AreaSchema.partial().safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "参数错误", details: parsed.error.message });
    return;
  }
  const [row] = await db
    .update(chestAreas)
    .set({
      name: parsed.data.name ?? undefined,
      description: parsed.data.description ?? undefined,
      color: parsed.data.color ?? undefined,
      vertex1: parsed.data.vertex1 ?? undefined,
      vertex2: parsed.data.vertex2 ?? undefined,
      extendsFrom: parsed.data.extendsFrom ?? undefined,
    })
    .where(eq(chestAreas.id, id))
    .returning();
  if (!row) {
    res.status(404).json({ error: "找不到此区域" });
    return;
  }
  logEvent("system", `更新区域 #${id}：${row.name}`);
  res.json({ ok: true, area: row });
});

router.delete("/areas/:id", async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id)) {
    res.status(400).json({ error: "无效 ID" });
    return;
  }
  // Snapshots' area_id will be set to NULL via FK rule
  await db.delete(chestAreas).where(eq(chestAreas.id, id));
  logEvent("system", `已删除区域 #${id}`);
  res.json({ ok: true });
});

export default router;
