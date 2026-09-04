const form = document.getElementById("task-form");
const input = document.getElementById("task-input");
const list = document.getElementById("task-list");
const stats = document.getElementById("stats");
const emptyState = document.getElementById("empty-state");

async function api(path, options) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok && res.status !== 204) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json();
}

function render(tasks) {
  list.innerHTML = "";
  emptyState.hidden = tasks.length > 0;

  for (const task of tasks) {
    const li = document.createElement("li");
    li.className = `task${task.done ? " task--done" : ""}`;
    li.dataset.id = task.id;

    const check = document.createElement("input");
    check.type = "checkbox";
    check.className = "task__check";
    check.checked = task.done;
    check.setAttribute("aria-label", `Mark "${task.title}" as done`);
    check.addEventListener("change", () => toggleTask(task.id));

    const title = document.createElement("span");
    title.className = "task__title";
    title.textContent = task.title;

    const del = document.createElement("button");
    del.className = "task__delete";
    del.type = "button";
    del.textContent = "\u00d7";
    del.setAttribute("aria-label", `Delete "${task.title}"`);
    del.addEventListener("click", () => deleteTask(task.id));

    li.append(check, title, del);
    list.appendChild(li);
  }

  const done = tasks.filter((t) => t.done).length;
  stats.innerHTML = `<span><strong>${tasks.length}</strong> total</span><span><strong>${done}</strong> done</span><span><strong>${tasks.length - done}</strong> remaining</span>`;
}

async function refresh() {
  render(await api("/api/tasks"));
}

async function addTask(title) {
  await api("/api/tasks", { method: "POST", body: JSON.stringify({ title }) });
  await refresh();
}

async function toggleTask(id) {
  await api(`/api/tasks/${id}`, { method: "PATCH" });
  await refresh();
}

async function deleteTask(id) {
  await api(`/api/tasks/${id}`, { method: "DELETE" });
  await refresh();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = input.value.trim();
  if (!title) return;
  input.value = "";
  try {
    await addTask(title);
  } catch (err) {
    alert(err.message);
  }
  input.focus();
});

refresh().catch((err) => {
  stats.textContent = `Could not load tasks: ${err.message}`;
});
