#!/usr/bin/env python3
"""Acceso de la nube a la app FlowHelen Panel (https://flowhelen-panel.fly.dev).

La llave NUNCA va en el chat ni en git: se guarda como variable del entorno de
la nube FLOWHELEN_PANEL_KEY (Snailer la pone en la configuración del entorno).
Se envía en la cabecera x-flota-key, como hacen las sesiones del PC.

  python tools/panel.py GET /api/health                      (público)
  python tools/panel.py GET "/api/metodos?slug=<slug>"
  python tools/panel.py POST /api/mama/record --datos '{...}' --escribir

Por defecto solo lectura (GET). Cualquier escritura exige --escribir, a
propósito: no se cambia nada que ya funciona sin la orden de Snailer.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("FLOWHELEN_PANEL_URL", "https://flowhelen-panel.fly.dev").rstrip("/")


class SinRedireccion(urllib.request.HTTPRedirectHandler):
    """Sin llave la app redirige a /login: se informa el 302 en vez de seguirlo."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


ABRIR = urllib.request.build_opener(SinRedireccion()).open


def llamar(metodo: str, ruta: str, datos: str | None = None) -> tuple[int, str]:
    cabeceras = {"Accept": "application/json", "User-Agent": "claude-nube/1.0"}
    llave = os.environ.get("FLOWHELEN_PANEL_KEY")
    if llave:
        cabeceras["x-flota-key"] = llave
    cuerpo = None
    if datos is not None:
        cuerpo = datos.encode("utf-8")
        cabeceras["Content-Type"] = "application/json"
    pedido = urllib.request.Request(BASE + ruta, data=cuerpo, method=metodo, headers=cabeceras)
    try:
        with ABRIR(pedido, timeout=60) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("metodo", choices=["GET", "POST", "PATCH", "DELETE"])
    ap.add_argument("ruta", help="ruta que empieza por /, p. ej. /api/health")
    ap.add_argument("--datos", help="cuerpo JSON para POST/PATCH")
    ap.add_argument("--escribir", action="store_true", help="autoriza una escritura (orden de Snailer)")
    a = ap.parse_args(argv)
    if a.metodo != "GET" and not a.escribir:
        print("Escritura bloqueada: añade --escribir solo con orden de Snailer.", file=sys.stderr)
        return 3
    if not a.ruta.startswith("/"):
        ap.error("la ruta empieza por /")
    if not os.environ.get("FLOWHELEN_PANEL_KEY") and a.ruta != "/api/health":
        print("Falta FLOWHELEN_PANEL_KEY en el entorno de la nube: sin ella la app responde con el login.",
              file=sys.stderr)
    estado, texto = llamar(a.metodo, a.ruta, a.datos)
    try:
        print(json.dumps(json.loads(texto), ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(texto[:2000])
    if estado in (401, 403) or (estado == 302):
        print(f"HTTP {estado}: la llave falta o no tiene permiso para esta ruta.", file=sys.stderr)
    return 0 if 200 <= estado < 300 else 1


if __name__ == "__main__":
    sys.exit(main())
