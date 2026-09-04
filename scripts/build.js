import { build } from "esbuild";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");

/**
 * Bundle and minify the browser entrypoint into public/dist. This gives the
 * project a real, verifiable build step for the Cloud Agent environment.
 */
await build({
  entryPoints: [join(root, "public", "app.js")],
  bundle: true,
  minify: true,
  format: "esm",
  target: ["es2020"],
  outfile: join(root, "public", "dist", "app.min.js"),
  logLevel: "info",
});

console.log("Build complete: public/dist/app.min.js");
