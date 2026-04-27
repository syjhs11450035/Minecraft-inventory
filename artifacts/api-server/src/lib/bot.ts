import mineflayer from "mineflayer";
import { logger } from "./logger";
import { logEvent } from "./event-log";
import { tryHandleAIMessage } from "./ai";

export type BotStatus =
  | "disconnected"
  | "connecting"
  | "connected"
  | "spawned"
  | "error";

export interface BotConfig {
  host: string;
  port: number;
  username: string;
  version?: string;
  auth?: "offline" | "microsoft";
}

interface BotState {
  status: BotStatus;
  message: string;
  config: BotConfig | null;
  bot: any | null;
  spawnedAt: number | null;
  position: { x: number; y: number; z: number; dimension: string } | null;
  health: number | null;
  food: number | null;
}

const state: BotState = {
  status: "disconnected",
  message: "未连接",
  config: null,
  bot: null,
  spawnedAt: null,
  position: null,
  health: null,
  food: null,
};

export function getBotState() {
  return {
    status: state.status,
    message: state.message,
    config: state.config,
    spawnedAt: state.spawnedAt,
    position: state.position,
    health: state.health,
    food: state.food,
  };
}

export function getBot(): any {
  return state.bot;
}

export async function connectBot(cfg: BotConfig): Promise<void> {
  await disconnectBot();

  state.status = "connecting";
  state.message = `正在连线到 ${cfg.host}:${cfg.port}…`;
  state.config = cfg;
  logEvent("system", `尝试连线 ${cfg.host}:${cfg.port}（账号 ${cfg.username}, ${cfg.auth || "offline"}）`);

  return new Promise((resolve, reject) => {
    let resolved = false;
    try {
      const createOpts: any = {
        host: cfg.host,
        port: cfg.port,
        username: cfg.username,
        auth: cfg.auth || "offline",
        hideErrors: false,
      };
      if (cfg.version) {
        createOpts.version = cfg.version;
      }
      const bot = mineflayer.createBot(createOpts);

      state.bot = bot;

      bot.once("spawn", () => {
        state.status = "spawned";
        state.message = "已上线，等待指令";
        state.spawnedAt = Date.now();
        logEvent("info", `机器人已出生于游戏世界`);
        if (bot.entity?.position) {
          state.position = {
            x: Math.floor(bot.entity.position.x),
            y: Math.floor(bot.entity.position.y),
            z: Math.floor(bot.entity.position.z),
            dimension: bot.game?.dimension || "overworld",
          };
        }
        state.health = bot.health ?? null;
        state.food = bot.food ?? null;
        logger.info({ host: cfg.host, port: cfg.port }, "bot spawned");
        if (!resolved) {
          resolved = true;
          resolve();
        }
      });

      bot.on("login", () => {
        state.status = "connected";
        state.message = "已登录，等待出生点…";
        logEvent("info", "已登录服务器");
      });

      bot.on("messagestr", (message: string) => {
        const text = String(message || "").slice(0, 500);
        if (text.trim()) logEvent("chat", text);
        try {
          tryHandleAIMessage(bot, text);
        } catch {
          // ignore AI dispatch errors
        }
      });

      bot.on("health", () => {
        state.health = bot.health ?? null;
        state.food = bot.food ?? null;
      });

      bot.on("move", () => {
        if (bot.entity?.position) {
          state.position = {
            x: Math.floor(bot.entity.position.x),
            y: Math.floor(bot.entity.position.y),
            z: Math.floor(bot.entity.position.z),
            dimension: bot.game?.dimension || state.position?.dimension || "overworld",
          };
        }
      });

      bot.on("kicked", (reason: string) => {
        state.status = "error";
        state.message = `被服务器踢出：${reason}`;
        state.bot = null;
        logger.warn({ reason }, "bot kicked");
        logEvent("error", `被服务器踢出：${reason}`);
        if (!resolved) {
          resolved = true;
          reject(new Error(`被踢出：${reason}`));
        }
      });

      bot.on("error", (err: Error) => {
        state.status = "error";
        state.message = `错误：${err.message}`;
        logger.error({ err }, "bot error");
        logEvent("error", `连线错误：${err.message}`);
        if (!resolved) {
          resolved = true;
          reject(err);
        }
      });

      bot.on("end", (reason: string) => {
        if (state.status !== "error") {
          state.status = "disconnected";
          state.message = `连线已结束：${reason || ""}`;
        }
        state.bot = null;
        state.spawnedAt = null;
        logger.info({ reason }, "bot ended");
        logEvent("system", `连线结束：${reason || "(未知原因)"}`);
      });

      setTimeout(() => {
        if (!resolved) {
          resolved = true;
          reject(new Error("连线超时（30 秒）"));
        }
      }, 30_000);
    } catch (err: any) {
      state.status = "error";
      state.message = `建立连线失败：${err.message}`;
      reject(err);
    }
  });
}

export async function disconnectBot(): Promise<void> {
  if (state.bot) {
    try {
      state.bot.quit("Streamlit 介面要求中断");
    } catch {
      // ignore
    }
    state.bot = null;
    logEvent("system", "用户主动离线");
  }
  state.status = "disconnected";
  state.message = "已离线";
  state.spawnedAt = null;
}

export async function sendChat(message: string): Promise<void> {
  if (!state.bot) throw new Error("机器人未上线");
  state.bot.chat(message);
  logEvent("chat", `[我] ${message}`);
}

export async function findNearbyChest(
  range = 6,
): Promise<{ x: number; y: number; z: number; name: string } | null> {
  const bot = state.bot;
  if (!bot) throw new Error("机器人未上线");
  const mcData = (await import("minecraft-data")).default(bot.version);
  const chestNames = [
    "chest",
    "trapped_chest",
    "barrel",
    "ender_chest",
  ];
  const ids = chestNames
    .map((n) => mcData.blocksByName[n]?.id)
    .filter((id: number | undefined) => id !== undefined);
  if (ids.length === 0) return null;
  const block = bot.findBlock({ matching: ids, maxDistance: range });
  if (!block) return null;
  const def = mcData.blocks[block.type];
  return {
    x: block.position.x,
    y: block.position.y,
    z: block.position.z,
    name: def?.displayName || def?.name || "Container",
  };
}

export async function openNearbyChest(range = 6) {
  const bot = state.bot;
  if (!bot) throw new Error("机器人未上线");
  const target = await findNearbyChest(range);
  if (!target) throw new Error(`附近 ${range} 格内找不到箱子/木桶/末影箱`);

  const block = bot.blockAt(
    bot.entity.position.constructor
      ? new bot.entity.position.constructor(target.x, target.y, target.z)
      : { x: target.x, y: target.y, z: target.z },
  );
  if (!block) throw new Error("无法定位箱子方块");

  const container = await bot.openContainer(block);
  return { container, target };
}
