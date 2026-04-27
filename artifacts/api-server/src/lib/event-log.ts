export type EventLevel = "info" | "warn" | "error" | "chat" | "system" | "ai";

export interface EventEntry {
  ts: number;
  level: EventLevel;
  message: string;
}

const MAX = 300;
const buffer: EventEntry[] = [];

export function logEvent(level: EventLevel, message: string) {
  buffer.push({ ts: Date.now(), level, message });
  if (buffer.length > MAX) buffer.splice(0, buffer.length - MAX);
}

export function getEvents(limit = 200): EventEntry[] {
  if (limit >= buffer.length) return [...buffer];
  return buffer.slice(buffer.length - limit);
}

export function clearEvents() {
  buffer.length = 0;
}
