#!/usr/bin/env python3
"""Lee una ficha PÚBLICA de TikTok Shop US por su ID (sin login ni API).

Sirve para auditar lo que ve el comprador: título, foto principal, categoría,
vendedor y, con --navegador, la galería completa, las variantes y una captura.
Es solo lectura: no toca la tienda.

  python tools/tiktok_pdp.py 1732659829281624379
  python tools/tiktok_pdp.py 1732659829281624379 --navegador --carpeta out/pdp

Si TikTok devuelve su "Security Check", el resultado es BLOQUEADO (no "no
existe"): reintenta más tarde o usa la API de la tienda (orquestador, cli=tiktok).
En la nube, el navegador pasa por el proxy de la sesión y solo confía en su CA.
"""
from __future__ import annotations

import argparse
import base64
import glob
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
BASE = "https://shop.tiktok.com/us/pdp/"
CA_PROXY = "/root/.ccr/agent-proxy-ca.crt"
IMG_RE = re.compile(r"https://p\d+-oec[^\"'\s)]+?/([0-9a-f]{32})~tplv[^\"'\s)]*")


def meta(h: str, prop: str) -> str | None:
    m = re.search(r'<meta[^>]+(?:property|name)="%s"[^>]+content="([^"]*)"' % re.escape(prop), h)
    return html.unescape(m.group(1)) if m else None


def datos_ssr(h: str) -> dict:
    m = re.search(r'<script type="application/json" id="__MODERN_ROUTER_DATA__">(.*?)</script>', h, re.S)
    if not m:
        return {}
    try:
        carga = json.loads(m.group(1))["loaderData"]
        pagina = next(v for k, v in carga.items() if k.endswith("/page") and v)
        info = pagina["page_config"]["global_data"]["product_info"]
        return {
            "categorias": [c.get("category_name") for c in info.get("categories", [])],
            "vendedor_id": info.get("product_info", {}).get("seller_id"),
        }
    except (KeyError, StopIteration, TypeError, json.JSONDecodeError):
        return {}


def leer_simple(pid: str) -> dict:
    pedido = urllib.request.Request(BASE + pid, headers={"User-Agent": UA, "Accept-Language": "en-US"})
    with urllib.request.urlopen(pedido, timeout=45) as r:
        h = r.read().decode("utf-8", "ignore")
        url = r.geturl()
    titulo_html = re.search(r"<title>([^<]*)</title>", h)
    if titulo_html and "Security Check" in titulo_html.group(1):
        return {"id": pid, "estado": "BLOQUEADO", "motivo": "TikTok pidió Security Check", "url": url}
    return {
        "id": pid,
        "estado": "OK",
        "url": url,
        "titulo": meta(h, "og:title"),
        "foto_principal": meta(h, "og:image"),
        "descripcion_meta": meta(h, "og:description"),
        **datos_ssr(h),
    }


def spki_proxy() -> str | None:
    if not Path(CA_PROXY).exists():
        return None
    pub = subprocess.run(["openssl", "x509", "-in", CA_PROXY, "-pubkey", "-noout"],
                         capture_output=True, check=True).stdout
    der = subprocess.run(["openssl", "pkey", "-pubin", "-outform", "der"], input=pub,
                         capture_output=True, check=True).stdout
    return base64.b64encode(hashlib.sha256(der).digest()).decode()


def leer_navegador(pid: str, carpeta: Path) -> dict:
    from playwright.sync_api import sync_playwright

    carpeta.mkdir(parents=True, exist_ok=True)
    args = ["--no-sandbox"]
    spki = spki_proxy()
    if spki:
        args.append("--ignore-certificate-errors-spki-list=" + spki)
    opciones = {"headless": True, "args": args}
    chrome = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
    if chrome:
        opciones["executable_path"] = chrome[-1]
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        opciones["proxy"] = {"server": proxy}
    with sync_playwright() as p:
        navegador = p.chromium.launch(**opciones)
        pagina = navegador.new_page(user_agent=UA, locale="en-US", viewport={"width": 1366, "height": 900})
        pagina.goto(BASE + pid, wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(7000)
        titulo = pagina.title()
        h = pagina.content()
        pagina.screenshot(path=str(carpeta / f"{pid}.png"))
        texto = pagina.inner_text("body")
        navegador.close()
    (carpeta / f"{pid}.html").write_text(h, encoding="utf-8")
    if "Security Check" in titulo:
        return {"id": pid, "estado": "BLOQUEADO", "motivo": "TikTok pidió Security Check"}
    fotos, vistas = [], set()
    for m in IMG_RE.finditer(html.unescape(h)):
        if m.group(1) not in vistas and ("800:800" in m.group(0) or "crop" in m.group(0)):
            vistas.add(m.group(1))
            fotos.append(m.group(0))
    lineas = [x.strip() for x in texto.splitlines() if x.strip()]
    vendidos = next((x for x in lineas if re.fullmatch(r"[\d.,]+K?\+? sold", x)), None)
    precio = next((x for x in lineas if re.fullmatch(r"\$[\d.,]+", x)), None)
    return {"id": pid, "estado": "OK", "titulo_pagina": titulo, "fotos_galeria": fotos,
            "vendidos_texto": vendidos, "precio_texto": precio,
            "captura": str(carpeta / f"{pid}.png")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="+", help="IDs de producto de TikTok Shop")
    ap.add_argument("--navegador", action="store_true", help="renderiza con Chromium (galería y captura)")
    ap.add_argument("--carpeta", default="out/pdp")
    a = ap.parse_args(argv)
    bloqueados = 0
    for pid in a.ids:
        try:
            r = leer_simple(pid)
            if a.navegador and r.get("estado") == "OK":
                r.update(leer_navegador(pid, Path(a.carpeta)))
        except Exception as e:  # el error real, nunca un "no se pudo" a secas
            r = {"id": pid, "estado": "ERROR", "error": f"{type(e).__name__}: {e}"}
        bloqueados += r.get("estado") != "OK"
        print(json.dumps(r, ensure_ascii=False, indent=2))
    return 1 if bloqueados else 0


if __name__ == "__main__":
    sys.exit(main())
