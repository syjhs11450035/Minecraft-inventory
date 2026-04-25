import { Router, type IRouter } from "express";
import { z } from "zod/v4";
import {
  connectBot,
  disconnectBot,
  getBot,
  getBotState,
  sendChat,
  findNearbyChest,
} from "../lib/bot";
import { getEvents, clearEvents } from "../lib/event-log";

const router: IRouter = Router();

const ConnectSchema = z.object({
  host: z.string().min(1),
  port: z.number().int().min(1).max(65535).default(25565),
  username: z.string().min(1).max(32),
  version: z.string().optional(),
  auth: z.enum(["offline", "microsoft"]).optional(),
});

router.get("/bot/status", (_req, res) => {
  res.json(getBotState());
});

router.post("/bot/connect", async (req, res) => {
  const parsed = ConnectSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "参数错误", details: parsed.error.message });
    return;
  }
  try {
    await connectBot(parsed.data);
    res.json({ ok: true, state: getBotState() });
  } catch (err: any) {
    res.status(500).json({ error: err.message, state: getBotState() });
  }
});

router.post("/bot/disconnect", async (_req, res) => {
  await disconnectBot();
  res.json({ ok: true, state: getBotState() });
});

router.post("/bot/chat", async (req, res) => {
  const msg = String(req.body?.message ?? "").trim();
  if (!msg) {
    res.status(400).json({ error: "讯息不可为空" });
    return;
  }
  try {
    await sendChat(msg);
    res.json({ ok: true });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

router.get("/bot/nearby-chest", async (req, res) => {
  const range = Math.min(
    32,
    Math.max(1, Number(req.query.range ?? 6) || 6),
  );
  try {
    const target = await findNearbyChest(range);
    res.json({ found: Boolean(target), target });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

router.get("/bot/logs", (req, res) => {
  const limit = Math.min(300, Math.max(1, Number(req.query.limit ?? 200) || 200));
  res.json({ entries: getEvents(limit) });
});

router.delete("/bot/logs", (_req, res) => {
  clearEvents();
  res.json({ ok: true });
});

router.get("/bot/inventory-preview", async (_req, res) => {
  const bot = getBot();
  if (!bot) {
    res.status(400).json({ error: "机器人未上线" });
    return;
  }
  try {
    const items = (bot.inventory.items() as any[]).map((it) => ({
      name: it.name,
      displayName: it.displayName,
      count: it.count,
      slot: it.slot,
    }));
    res.json({ items });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
