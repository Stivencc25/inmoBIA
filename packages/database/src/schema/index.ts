import {
  pgTable,
  uuid,
  varchar,
  text,
  integer,
  decimal,
  boolean,
  timestamp,
  jsonb,
  pgEnum,
  index,
} from "drizzle-orm/pg-core";

// ─── Enums ────────────────────────────────────────────────────────────────────

export const agencyPlanEnum = pgEnum("agency_plan", ["free", "pro", "enterprise"]);

export const userRoleEnum = pgEnum("user_role", ["admin", "agent", "buyer", "renter"]);

export const propertyTypeEnum = pgEnum("property_type", [
  "house",
  "apartment",
  "office",
  "land",
  "commercial",
  "penthouse",
]);

export const transactionTypeEnum = pgEnum("transaction_type", ["sale", "rent", "both"]);

export const propertyStatusEnum = pgEnum("property_status", [
  "draft",
  "active",
  "reserved",
  "sold",
  "rented",
  "archived",
]);

export const mediaTypeEnum = pgEnum("media_type", ["photo", "video", "tour360"]);

export const mediaCategoryEnum = pgEnum("media_category", [
  "exterior",
  "living_room",
  "kitchen",
  "bedroom",
  "bathroom",
  "other",
]);

export const visitTypeEnum = pgEnum("visit_type", ["in_person", "virtual"]);

export const visitStatusEnum = pgEnum("visit_status", [
  "scheduled",
  "confirmed",
  "completed",
  "cancelled",
]);

export const clientTypeEnum = pgEnum("client_type", ["buyer", "renter", "investor"]);

export const clientStatusEnum = pgEnum("client_status", [
  "lead",
  "prospect",
  "negotiating",
  "closed",
  "lost",
]);

export const messageRoleEnum = pgEnum("message_role", ["user", "assistant"]);

// ─── Agencies ─────────────────────────────────────────────────────────────────

export const agencies = pgTable("agencies", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: varchar("name", { length: 255 }).notNull(),
  slug: varchar("slug", { length: 100 }).notNull().unique(),
  logoUrl: text("logo_url"),
  subdomain: varchar("subdomain", { length: 100 }).unique(),
  plan: agencyPlanEnum("plan").notNull().default("free"),
  settings: jsonb("settings").default({}),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

// ─── Users ────────────────────────────────────────────────────────────────────

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  agencyId: uuid("agency_id").references(() => agencies.id, { onDelete: "cascade" }),
  role: userRoleEnum("role").notNull().default("buyer"),
  email: varchar("email", { length: 255 }).notNull().unique(),
  name: varchar("name", { length: 255 }).notNull(),
  phone: varchar("phone", { length: 50 }),
  avatarUrl: text("avatar_url"),
  preferences: jsonb("preferences").default({}),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

// ─── Properties ───────────────────────────────────────────────────────────────

export const properties = pgTable(
  "properties",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    agencyId: uuid("agency_id")
      .notNull()
      .references(() => agencies.id, { onDelete: "cascade" }),
    agentId: uuid("agent_id")
      .notNull()
      .references(() => users.id),
    title: varchar("title", { length: 255 }).notNull(),
    description: text("description"),
    descriptionAi: text("description_ai"),
    type: propertyTypeEnum("type").notNull(),
    transactionType: transactionTypeEnum("transaction_type").notNull(),
    status: propertyStatusEnum("status").notNull().default("draft"),
    price: decimal("price", { precision: 14, scale: 2 }).notNull(),
    currency: varchar("currency", { length: 10 }).notNull().default("MXN"),
    pricePerSqm: decimal("price_per_sqm", { precision: 12, scale: 2 }),
    areaTotal: decimal("area_total", { precision: 10, scale: 2 }),
    areaBuilt: decimal("area_built", { precision: 10, scale: 2 }),
    bedrooms: integer("bedrooms"),
    bathrooms: integer("bathrooms"),
    parking: integer("parking"),
    features: jsonb("features").default({}),
    address: text("address"),
    city: varchar("city", { length: 100 }),
    neighborhood: varchar("neighborhood", { length: 100 }),
    state: varchar("state", { length: 100 }),
    postalCode: varchar("postal_code", { length: 20 }),
    // NOTE: location (GEOMETRY POINT) y embedding (VECTOR 1536) se agregan via migracion SQL raw
    // cuando se habiliten las extensiones PostGIS y pgvector en Supabase
    viewsCount: integer("views_count").notNull().default(0),
    favoritesCount: integer("favorites_count").notNull().default(0),
    publishedAt: timestamp("published_at"),
    createdAt: timestamp("created_at").notNull().defaultNow(),
    updatedAt: timestamp("updated_at").notNull().defaultNow(),
  },
  (table) => [
    index("properties_agency_id_idx").on(table.agencyId),
    index("properties_agent_id_idx").on(table.agentId),
    index("properties_status_idx").on(table.status),
    index("properties_city_idx").on(table.city),
  ]
);

// ─── Property Media ───────────────────────────────────────────────────────────

export const propertyMedia = pgTable("property_media", {
  id: uuid("id").primaryKey().defaultRandom(),
  propertyId: uuid("property_id")
    .notNull()
    .references(() => properties.id, { onDelete: "cascade" }),
  url: text("url").notNull(),
  thumbnailUrl: text("thumbnail_url"),
  type: mediaTypeEnum("type").notNull().default("photo"),
  category: mediaCategoryEnum("category").default("other"),
  altText: text("alt_text"),
  sortOrder: integer("sort_order").notNull().default(0),
  isCover: boolean("is_cover").notNull().default(false),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

// ─── Valuations (AVM) ─────────────────────────────────────────────────────────

export const valuations = pgTable("valuations", {
  id: uuid("id").primaryKey().defaultRandom(),
  propertyId: uuid("property_id")
    .notNull()
    .references(() => properties.id, { onDelete: "cascade" }),
  estimatedMin: decimal("estimated_min", { precision: 14, scale: 2 }),
  estimatedMax: decimal("estimated_max", { precision: 14, scale: 2 }),
  estimatedValue: decimal("estimated_value", { precision: 14, scale: 2 }),
  confidenceScore: decimal("confidence_score", { precision: 4, scale: 3 }),
  modelVersion: varchar("model_version", { length: 50 }),
  comparablesUsed: jsonb("comparables_used").default([]),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

// ─── Clients ──────────────────────────────────────────────────────────────────

export const clients = pgTable("clients", {
  id: uuid("id").primaryKey().defaultRandom(),
  agencyId: uuid("agency_id")
    .notNull()
    .references(() => agencies.id, { onDelete: "cascade" }),
  assignedAgentId: uuid("assigned_agent_id").references(() => users.id),
  name: varchar("name", { length: 255 }).notNull(),
  email: varchar("email", { length: 255 }),
  phone: varchar("phone", { length: 50 }),
  type: clientTypeEnum("type").notNull().default("buyer"),
  status: clientStatusEnum("status").notNull().default("lead"),
  budgetMin: decimal("budget_min", { precision: 14, scale: 2 }),
  budgetMax: decimal("budget_max", { precision: 14, scale: 2 }),
  requirements: jsonb("requirements").default({}),
  source: varchar("source", { length: 50 }),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

// ─── Visits ───────────────────────────────────────────────────────────────────

export const visits = pgTable("visits", {
  id: uuid("id").primaryKey().defaultRandom(),
  propertyId: uuid("property_id")
    .notNull()
    .references(() => properties.id),
  clientId: uuid("client_id")
    .notNull()
    .references(() => clients.id),
  agentId: uuid("agent_id")
    .notNull()
    .references(() => users.id),
  type: visitTypeEnum("type").notNull().default("in_person"),
  status: visitStatusEnum("status").notNull().default("scheduled"),
  scheduledAt: timestamp("scheduled_at").notNull(),
  durationMinutes: integer("duration_minutes").default(60),
  notes: text("notes"),
  feedbackScore: integer("feedback_score"),
  feedbackNotes: text("feedback_notes"),
  meetingUrl: text("meeting_url"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

// ─── Conversations & Messages (chatbot IA) ────────────────────────────────────

export const conversations = pgTable("conversations", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: uuid("user_id").references(() => users.id),
  sessionId: varchar("session_id", { length: 255 }),
  context: jsonb("context").default({}),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const messages = pgTable("messages", {
  id: uuid("id").primaryKey().defaultRandom(),
  conversationId: uuid("conversation_id")
    .notNull()
    .references(() => conversations.id, { onDelete: "cascade" }),
  role: messageRoleEnum("role").notNull(),
  content: text("content").notNull(),
  metadata: jsonb("metadata").default({}),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

// ─── Saved Searches & Favorites ───────────────────────────────────────────────

export const savedSearches = pgTable("saved_searches", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: uuid("user_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  name: varchar("name", { length: 255 }),
  filters: jsonb("filters").notNull().default({}),
  alertEnabled: boolean("alert_enabled").notNull().default(false),
  alertFrequency: varchar("alert_frequency", { length: 50 }).default("weekly"),
  lastNotifiedAt: timestamp("last_notified_at"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const favorites = pgTable("favorites", {
  userId: uuid("user_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  propertyId: uuid("property_id")
    .notNull()
    .references(() => properties.id, { onDelete: "cascade" }),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});
