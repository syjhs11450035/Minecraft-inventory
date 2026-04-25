import {
  pgTable,
  serial,
  text,
  integer,
  timestamp,
  boolean,
} from "drizzle-orm/pg-core";

export const chestAreas = pgTable("chest_areas", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description"),
  color: text("color"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

export const containerSnapshots = pgTable("container_snapshots", {
  id: serial("id").primaryKey(),
  takenAt: timestamp("taken_at", { withTimezone: true }).defaultNow().notNull(),
  sourceType: text("source_type").notNull(),
  sourceKey: text("source_key").notNull(),
  label: text("label").notNull(),
  dimension: text("dimension"),
  x: integer("x"),
  y: integer("y"),
  z: integer("z"),
  notes: text("notes"),
  areaId: integer("area_id").references(() => chestAreas.id, {
    onDelete: "set null",
  }),
});

export const snapshotItems = pgTable("snapshot_items", {
  id: serial("id").primaryKey(),
  snapshotId: integer("snapshot_id")
    .references(() => containerSnapshots.id, { onDelete: "cascade" })
    .notNull(),
  itemName: text("item_name").notNull(),
  displayName: text("display_name").notNull(),
  count: integer("count").notNull(),
  stackSize: integer("stack_size").notNull().default(64),
  container: text("container").notNull().default("main"),
  isShulker: boolean("is_shulker").notNull().default(false),
});

export const botState = pgTable("bot_state", {
  id: serial("id").primaryKey(),
  host: text("host"),
  port: integer("port"),
  username: text("username"),
  version: text("version"),
  status: text("status").notNull().default("disconnected"),
  message: text("message"),
  updatedAt: timestamp("updated_at", { withTimezone: true })
    .defaultNow()
    .notNull(),
});

export type ChestArea = typeof chestAreas.$inferSelect;
export type ContainerSnapshot = typeof containerSnapshots.$inferSelect;
export type SnapshotItem = typeof snapshotItems.$inferSelect;
export type BotStateRow = typeof botState.$inferSelect;
