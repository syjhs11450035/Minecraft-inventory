import { Router, type IRouter } from "express";
import {
  getSettings,
  reloadSettings,
  settingsFilePath,
  updateSettings,
} from "../lib/settings";
import { clearAIHistory, getAIHistory } from "../lib/ai";

const router: IRouter = Router();

router.get("/settings", (_req, res) => {
  res.json(getSettings());
});

router.patch("/settings", (req, res) => {
  const body = req.body || {};
  const patch: any = {};

  if (body.connection && typeof body.connection === "object") {
    const c = body.connection;
    patch.connection = {};
    if (typeof c.host === "string") patch.connection.host = c.host;
    if (typeof c.port === "number") patch.connection.port = c.port;
    if (typeof c.username === "string") patch.connection.username = c.username;
    if (typeof c.version === "string") patch.connection.version = c.version;
    if (c.auth === "offline" || c.auth === "microsoft")
      patch.connection.auth = c.auth;
  }

  if (body.ai && typeof body.ai === "object") {
    patch.ai = {};
    if (typeof body.ai.enabled === "boolean") patch.ai.enabled = body.ai.enabled;
    if (typeof body.ai.model === "string") patch.ai.model = body.ai.model;
    if (typeof body.ai.systemPrompt === "string")
      patch.ai.systemPrompt = body.ai.systemPrompt;
    if (typeof body.ai.replyInChat === "boolean")
      patch.ai.replyInChat = body.ai.replyInChat;
  }

  if (body.htmlServer && typeof body.htmlServer === "object") {
    patch.htmlServer = {};
    if (typeof body.htmlServer.enabled === "boolean")
      patch.htmlServer.enabled = body.htmlServer.enabled;
    if (typeof body.htmlServer.port === "number")
      patch.htmlServer.port = body.htmlServer.port;
  }

  if (body.ui && typeof body.ui === "object") {
    patch.ui = {};
    if (typeof body.ui.autoRefresh === "boolean")
      patch.ui.autoRefresh = body.ui.autoRefresh;
  }

  res.json(updateSettings(patch));
});

router.post("/settings/reload", (_req, res) => {
  res.json({ ok: true, settings: reloadSettings(), path: settingsFilePath() });
});

router.get("/settings/file", (_req, res) => {
  res.json({ path: settingsFilePath() });
});

router.get("/ai/history", (_req, res) => {
  res.json({ history: getAIHistory() });
});

router.delete("/ai/history", (_req, res) => {
  clearAIHistory();
  res.json({ ok: true });
});

export default router;
