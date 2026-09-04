import { randomUUID } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";

/**
 * A tiny file-backed task store. State is kept in memory and mirrored to a
 * JSON file so tasks survive a server restart during local development.
 * The store degrades gracefully to memory-only if the file cannot be read.
 */
export class TaskStore {
  constructor(filePath) {
    this.filePath = filePath;
    this.tasks = [];
    this.#load();
  }

  #load() {
    if (!this.filePath || !existsSync(this.filePath)) return;
    try {
      const parsed = JSON.parse(readFileSync(this.filePath, "utf8"));
      if (Array.isArray(parsed)) this.tasks = parsed;
    } catch {
      // Corrupt or unreadable file: start empty rather than crashing.
      this.tasks = [];
    }
  }

  #persist() {
    if (!this.filePath) return;
    mkdirSync(dirname(this.filePath), { recursive: true });
    writeFileSync(this.filePath, JSON.stringify(this.tasks, null, 2));
  }

  list() {
    return [...this.tasks].sort((a, b) => b.createdAt - a.createdAt);
  }

  add(title) {
    const trimmed = String(title ?? "").trim();
    if (!trimmed) {
      const err = new Error("Task title is required");
      err.status = 400;
      throw err;
    }
    const task = {
      id: randomUUID(),
      title: trimmed,
      done: false,
      createdAt: Date.now(),
    };
    this.tasks.push(task);
    this.#persist();
    return task;
  }

  toggle(id) {
    const task = this.tasks.find((t) => t.id === id);
    if (!task) return null;
    task.done = !task.done;
    this.#persist();
    return task;
  }

  remove(id) {
    const before = this.tasks.length;
    this.tasks = this.tasks.filter((t) => t.id !== id);
    const removed = this.tasks.length < before;
    if (removed) this.#persist();
    return removed;
  }

  clear() {
    this.tasks = [];
    this.#persist();
  }
}
