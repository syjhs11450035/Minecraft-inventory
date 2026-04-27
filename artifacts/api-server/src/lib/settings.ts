// 全域設定（持久化到 JSON 檔；由 Streamlit 透過 /api/settings 操作）
import {
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export interface ConnectionSettings {
  host: string;
  port: number;
  username: string;
  version: string;
  auth: "offline" | "microsoft";
}

export interface AISettings {
  enabled: boolean;
  model: string;
  systemPrompt: string;
  replyInChat: boolean;
}

export interface HtmlServerSettings {
  enabled: boolean;
  port: number;
}

export interface UISettings {
  autoRefresh: boolean;
}

export interface AppSettings {
  connection: ConnectionSettings;
  ai: AISettings;
  htmlServer: HtmlServerSettings;
  ui: UISettings;
}

const DEFAULTS: AppSettings = {
  connection: {
    host: "localhost",
    port: 25565,
    username: "InvBot",
    version: "",
    auth: "offline",
  },
  ai: {
    enabled: false,
    model: "claude-sonnet-4-6",
    systemPrompt:
      "你是一個 Minecraft 機器人助手，回覆要簡短、繁體中文，最多兩句話。" +
      "如果使用者要求動作（例如「跟我來」「停下」「跳」），請先簡短回應再描述會做的事。",
    replyInChat: true,
  },
  htmlServer: {
    enabled: false,
    port: 8000,
  },
  ui: {
    autoRefresh: false,
  },
};

function findWorkspaceRoot(): string {
  let cur: string;
  try {
    cur = dirname(fileURLToPath(import.meta.url));
  } catch {
    cur = process.cwd();
  }
  for (let i = 0; i < 10; i++) {
    if (existsSync(join(cur, "pnpm-workspace.yaml"))) return cur;
    const parent = dirname(cur);
    if (parent === cur) break;
    cur = parent;
  }
  return process.cwd();
}

const SETTINGS_PATH = resolve(
  process.env.SETTINGS_PATH || join(findWorkspaceRoot(), "data/settings.json"),
);

function ensureDir(path: string): void {
  mkdirSync(dirname(path), { recursive: true });
}

function isPlainObject(v: unknown): v is Record<string, any> {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

function mergeDeep<T>(base: T, patch: any): T {
  if (!isPlainObject(patch)) return base;
  const out: any = isPlainObject(base) ? { ...(base as any) } : {};
  for (const k of Object.keys(patch)) {
    const baseVal: any = (base as any)?.[k];
    const patchVal: any = patch[k];
    if (isPlainObject(baseVal) && isPlainObject(patchVal)) {
      out[k] = mergeDeep(baseVal, patchVal);
    } else if (patchVal !== undefined) {
      out[k] = patchVal;
    }
  }
  return out;
}

function loadFromDisk(): AppSettings {
  try {
    if (!existsSync(SETTINGS_PATH)) {
      const fresh = JSON.parse(JSON.stringify(DEFAULTS)) as AppSettings;
      saveToDisk(fresh);
      return fresh;
    }
    const raw = readFileSync(SETTINGS_PATH, "utf8");
    const parsed = JSON.parse(raw);
    return mergeDeep(DEFAULTS, parsed);
  } catch {
    return JSON.parse(JSON.stringify(DEFAULTS)) as AppSettings;
  }
}

function saveToDisk(s: AppSettings): void {
  ensureDir(SETTINGS_PATH);
  writeFileSync(SETTINGS_PATH, JSON.stringify(s, null, 2), "utf8");
}

let settings: AppSettings = loadFromDisk();

export function getSettings(): AppSettings {
  return settings;
}

export function updateSettings(patch: any): AppSettings {
  settings = mergeDeep(settings, patch);
  try {
    saveToDisk(settings);
  } catch {
    // ignore disk errors – keep in-memory copy
  }
  return settings;
}

export function settingsFilePath(): string {
  return SETTINGS_PATH;
}

export function reloadSettings(): AppSettings {
  settings = loadFromDisk();
  return settings;
}
