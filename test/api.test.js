import test from "node:test";
import assert from "node:assert/strict";
import request from "supertest";
import { createApp } from "../src/app.js";
import { TaskStore } from "../src/store.js";

function appForTest() {
  return createApp({ store: new TaskStore(null) });
}

test("GET /api/health reports ok", async () => {
  const res = await request(appForTest()).get("/api/health");
  assert.equal(res.status, 200);
  assert.equal(res.body.status, "ok");
});

test("tasks start empty", async () => {
  const res = await request(appForTest()).get("/api/tasks");
  assert.equal(res.status, 200);
  assert.deepEqual(res.body, []);
});

test("POST /api/tasks creates a task", async () => {
  const app = appForTest();
  const res = await request(app).post("/api/tasks").send({ title: "Write tests" });
  assert.equal(res.status, 201);
  assert.equal(res.body.title, "Write tests");
  assert.equal(res.body.done, false);
  assert.ok(res.body.id);

  const list = await request(app).get("/api/tasks");
  assert.equal(list.body.length, 1);
});

test("POST /api/tasks rejects an empty title", async () => {
  const res = await request(appForTest()).post("/api/tasks").send({ title: "   " });
  assert.equal(res.status, 400);
  assert.match(res.body.error, /required/i);
});

test("PATCH /api/tasks/:id toggles done", async () => {
  const app = appForTest();
  const created = await request(app).post("/api/tasks").send({ title: "Toggle me" });
  const id = created.body.id;

  const toggled = await request(app).patch(`/api/tasks/${id}`);
  assert.equal(toggled.status, 200);
  assert.equal(toggled.body.done, true);

  const toggledBack = await request(app).patch(`/api/tasks/${id}`);
  assert.equal(toggledBack.body.done, false);
});

test("PATCH unknown id returns 404", async () => {
  const res = await request(appForTest()).patch("/api/tasks/does-not-exist");
  assert.equal(res.status, 404);
});

test("DELETE /api/tasks/:id removes a task", async () => {
  const app = appForTest();
  const created = await request(app).post("/api/tasks").send({ title: "Delete me" });
  const id = created.body.id;

  const del = await request(app).delete(`/api/tasks/${id}`);
  assert.equal(del.status, 204);

  const list = await request(app).get("/api/tasks");
  assert.equal(list.body.length, 0);
});

test("DELETE unknown id returns 404", async () => {
  const res = await request(appForTest()).delete("/api/tasks/nope");
  assert.equal(res.status, 404);
});
