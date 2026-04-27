// 全域設定（簡單 in-memory 儲存，由 Streamlit 設定分頁透過 /api/settings 操作）

export interface AppSettings {
  ai: {
    enabled: boolean;
    model: string;
    systemPrompt: string;
    replyInChat: boolean;
  };
}

const settings: AppSettings = {
  ai: {
    enabled: false,
    model: "claude-sonnet-4-6",
    systemPrompt:
      "你是一個 Minecraft 機器人助手，回覆要簡短、繁體中文，最多兩句話。" +
      "如果使用者要求動作（例如「跟我來」「停下」「跳」），請先簡短回應再描述會做的事。",
    replyInChat: true,
  },
};

export function getSettings(): AppSettings {
  return settings;
}

export function updateSettings(patch: Partial<AppSettings>): AppSettings {
  if (patch.ai) {
    settings.ai = { ...settings.ai, ...patch.ai };
  }
  return settings;
}
