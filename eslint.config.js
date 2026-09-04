import js from "@eslint/js";
import globals from "globals";

export default [
  {
    ignores: ["public/dist/**", "node_modules/**", "data/**"],
  },
  js.configs.recommended,
  {
    files: ["src/**/*.js", "scripts/**/*.js", "test/**/*.js"],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: "module",
      globals: { ...globals.node },
    },
  },
  {
    files: ["public/**/*.js"],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: "module",
      globals: { ...globals.browser },
    },
  },
];
