// AI 處理模組：監聽 ai! 前綴並呼叫 Anthropic
import Anthropic from "@anthropic-ai/sdk";
import { logEvent } from "./event-log";
import { getSettings } from "./settings";

const baseURL = process.env.AI_INTEGRATIONS_ANTHROPIC_BASE_URL;
const apiKey = process.env.AI_INTEGRATIONS_ANTHROPIC_API_KEY;

let client: Anthropic | null = null;
function getClient(): Anthropic | null {
  if (!baseURL || !apiKey) return null;
  if (!client) {
    client = new Anthropic({ baseURL, apiKey });
  }
  return client;
}

const ACTION_KEYWORDS: Array<{ pattern: RegExp; label: string; run: (bot: any) => void }> = [
  {
    pattern: /(跟我來|跟過來|follow|come)/i,
    label: "跟隨我",
    run: (bot) => {
      const owner = bot._lastSender;
      if (!owner) return;
      const target = bot.players?.[owner]?.entity;
      if (!target) return;
      try {
        bot.lookAt(target.position.offset(0, 1.6, 0));
      } catch {
        // ignore
      }
    },
  },
  {
    pattern: /(停下|stop|別動)/i,
    label: "停下動作",
    run: (bot) => {
      try {
        bot.clearControlStates?.();
      } catch {
        // ignore
      }
    },
  },
  {
    pattern: /(跳|jump)/i,
    label: "跳一下",
    run: (bot) => {
      try {
        bot.setControlState("jump", true);
        setTimeout(() => bot.setControlState("jump", false), 350);
      } catch {
        // ignore
      }
    },
  },
];

function detectAction(reply: string, bot: any): string | null {
  for (const { pattern, label, run } of ACTION_KEYWORDS) {
    if (pattern.test(reply)) {
      try {
        run(bot);
      } catch {
        // ignore
      }
      return label;
    }
  }
  return null;
}

interface HistoryMsg {
  role: "user" | "assistant";
  content: string;
}
const history: HistoryMsg[] = [];
const MAX_HISTORY = 12;

function pushHistory(msg: HistoryMsg): void {
  history.push(msg);
  while (history.length > MAX_HISTORY) history.shift();
}

export async function askAI(prompt: string, sender: string, bot: any): Promise<string> {
  const settings = getSettings();
  const c = getClient();
  if (!c) {
    return "（AI 未設定：缺少 Anthropic 整合金鑰）";
  }

  pushHistory({ role: "user", content: `${sender}：${prompt}` });

  try {
    const message = await c.messages.create({
      model: settings.ai.model || "claude-sonnet-4-6",
      max_tokens: 8192,
      system: settings.ai.systemPrompt,
      messages: history.map((h) => ({ role: h.role, content: h.content })),
    });
    const block = message.content[0];
    let reply =
      block && block.type === "text" ? block.text.trim() : "（AI 沒有回應）";
    if (reply.length > 220) reply = reply.slice(0, 217) + "…";
    pushHistory({ role: "assistant", content: reply });

    const actionLabel = detectAction(reply, bot);
    if (actionLabel) {
      logEvent("ai", `動作：${actionLabel}`);
    }
    return reply;
  } catch (err: any) {
    const msg = err?.message || String(err);
    logEvent("error", `AI 呼叫失敗：${msg}`);
    return `（AI 錯誤：${msg.slice(0, 100)}）`;
  }
}

export function clearAIHistory(): void {
  history.length = 0;
}

export function getAIHistory(): HistoryMsg[] {
  return [...history];
}

const AI_TRIGGER = /^(?:<([^>]+)>\s*)?ai!\s*(.+)$/i;

export function tryHandleAIMessage(bot: any, text: string): void {
  const settings = getSettings();
  if (!settings.ai.enabled) return;
  const m = text.match(AI_TRIGGER);
  if (!m) return;
  const sender = (m[1] || "未知").trim();
  const prompt = m[2].trim();
  if (!prompt) return;
  if (sender && bot?.username && sender === bot.username) return; // 忽略自己

  bot._lastSender = sender;
  logEvent("ai", `${sender} → ${prompt}`);

  askAI(prompt, sender, bot).then((reply) => {
    logEvent("ai", `[AI] ${reply}`);
    if (settings.ai.replyInChat && bot && typeof bot.chat === "function") {
      try {
        bot.chat(`@${sender} ${reply}`);
      } catch {
        // ignore
      }
    }
  });
}
