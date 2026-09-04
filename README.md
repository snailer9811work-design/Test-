# Test Task Manager

A small, modern full-stack demo used to exercise the Cloud Agent development
environment. It provides a REST API built with Express and a lightweight
vanilla-JavaScript frontend for managing a task list.

## Stack

- **Runtime:** Node.js (>= 20), ES modules
- **Server:** Express
- **Frontend:** static HTML/CSS/JS served by Express
- **Tests:** Node's built-in test runner (`node:test`) + `supertest`
- **Build:** `esbuild` bundles the browser entrypoint
- **Lint:** ESLint (flat config)

## Getting started

```bash
npm ci        # install dependencies (uses package-lock.json)
npm run dev   # start the dev server with auto-reload on http://localhost:3000
```

Then open http://localhost:3000 and add a task.

## Commands

| Command         | Description                                        |
| --------------- | -------------------------------------------------- |
| `npm start`     | Start the server                                   |
| `npm run dev`   | Start the server with `--watch` auto-reload        |
| `npm test`      | Run the automated test suite                       |
| `npm run lint`  | Lint the source with ESLint                        |
| `npm run build` | Bundle/minify the browser entrypoint into `dist/`  |

## API

| Method   | Path              | Description             |
| -------- | ----------------- | ----------------------- |
| `GET`    | `/api/health`     | Health check            |
| `GET`    | `/api/tasks`      | List tasks              |
| `POST`   | `/api/tasks`      | Create a task           |
| `PATCH`  | `/api/tasks/:id`  | Toggle a task's status  |
| `DELETE` | `/api/tasks/:id`  | Delete a task           |

## Configuration

| Variable    | Default              | Description                     |
| ----------- | -------------------- | ------------------------------- |
| `PORT`      | `3000`               | Port the server listens on      |
| `HOST`      | `0.0.0.0`            | Host interface to bind          |
| `DATA_FILE` | `data/tasks.json`    | Where tasks are persisted       |
