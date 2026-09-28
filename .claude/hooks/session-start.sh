#!/bin/bash
# Prepara cada sesión de Claude Code en la nube para las herramientas de tools/:
# Pillow (fotos de packs) y Playwright (leer fichas públicas de TikTok).
# Chromium ya viene instalado en /opt/pw-browsers: no se descarga ningún navegador.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

if ! python3 -c "import PIL, playwright" >/dev/null 2>&1; then
  PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 python3 -m pip install --quiet --disable-pip-version-check \
    --root-user-action=ignore -r requirements.txt
fi

python3 -c "import PIL, playwright; print('Sesión lista: Pillow', PIL.__version__, '· Playwright importable')"
