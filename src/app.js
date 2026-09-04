import express from "express";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { TaskStore } from "./store.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

/**
 * Build the Express application. The store is injected so tests can supply
 * an isolated in-memory store without touching the development data file.
 */
export function createApp({ store } = {}) {
  const app = express();
  const taskStore = store ?? new TaskStore(null);

  app.use(express.json());

  app.get("/api/health", (_req, res) => {
    res.json({ status: "ok", uptime: process.uptime() });
  });

  app.get("/api/tasks", (_req, res) => {
    res.json(taskStore.list());
  });

  app.post("/api/tasks", (req, res) => {
    try {
      const task = taskStore.add(req.body?.title);
      res.status(201).json(task);
    } catch (err) {
      res.status(err.status ?? 500).json({ error: err.message });
    }
  });

  app.patch("/api/tasks/:id", (req, res) => {
    const task = taskStore.toggle(req.params.id);
    if (!task) return res.status(404).json({ error: "Task not found" });
    res.json(task);
  });

  app.delete("/api/tasks/:id", (req, res) => {
    const removed = taskStore.remove(req.params.id);
    if (!removed) return res.status(404).json({ error: "Task not found" });
    res.status(204).end();
  });

  app.use(express.static(join(__dirname, "..", "public")));

  return app;
}
