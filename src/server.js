import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { createApp } from "./app.js";
import { TaskStore } from "./store.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

const PORT = Number(process.env.PORT) || 3000;
const HOST = process.env.HOST || "0.0.0.0";
const DATA_FILE = process.env.DATA_FILE || join(__dirname, "..", "data", "tasks.json");

const store = new TaskStore(DATA_FILE);
const app = createApp({ store });

app.listen(PORT, HOST, () => {
  console.log(`Task manager running at http://${HOST}:${PORT}`);
});
