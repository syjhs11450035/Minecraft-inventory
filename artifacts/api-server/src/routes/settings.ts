import { Router, type IRouter } from "express";
import { getSettings, updateSettings } from "../lib/settings";
import { clearAIHistory, getAIHistory } from "../lib/ai";

const router: IRouter = Router();

router.get("/settings", (_req, res) => {
  res.json(getSettings());
});

router.patch("/settings", (req, res) => {
  const patch: any = {};
  if (req.body?.ai && typeof req.body.ai === "object") {
    patch.ai = {};
    if (typeof req.body.ai.enabled === "boolean") patch.ai.enabled = req.body.ai.enabled;
    if (typeof req.body.ai.model === "string") patch.ai.model = req.body.ai.model;
    if (typeof req.body.ai.systemPrompt === "string")
      patch.ai.systemPrompt = req.body.ai.systemPrompt;
    if (typeof req.body.ai.replyInChat === "boolean")
      patch.ai.replyInChat = req.body.ai.replyInChat;
  }
  res.json(updateSettings(patch));
});

router.get("/ai/history", (_req, res) => {
  res.json({ history: getAIHistory() });
});

router.delete("/ai/history", (_req, res) => {
  clearAIHistory();
  res.json({ ok: true });
});

export default router;
