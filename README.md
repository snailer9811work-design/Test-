# Test- · Reglas y herramientas de Snailer para Claude Code en la nube

- `CLAUDE.md` — cómo trabajamos: las reglas del PC pasadas a la nube (se carga sola en cada sesión).
- `.claude/` — arranque de sesión: instala Pillow y Playwright si faltan (solo en la nube).
- `tools/` — `panel.py` (app FlowHelen Panel), `tiktok_pdp.py` (fichas públicas de TikTok Shop),
  `pack_foto.py` (fotos de fichas en pack).
- `docs/metodos/` — métodos nuevos en el formato de `SecondBrain/METODOS` (la copia canónica va a Drive).

Pruebas: `python -m unittest discover -s tests` · Lint: `ruff check tools tests`.

Nada de llaves, correos ni datos de dinero en este repositorio: es público. Las llaves van en las
variables del entorno de la nube (`FLOWHELEN_PANEL_KEY`).
