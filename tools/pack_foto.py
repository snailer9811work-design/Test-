#!/usr/bin/env python3
"""Fotos de fichas en PACK: la foto enseña las N unidades que trae ESA variante.

Regla de Snailer (28-sep-2026): si el producto se vende en pack, la foto
principal y la foto de CADA variante muestran la cantidad de ese pack.
La cantidad sale de la ficha del proveedor, nunca de la foto.

Tres órdenes:

  cuadrar   -> la foto del PROVEEDOR que ya enseña las N unidades, cuadrada y a
               1600x1600 con su mismo fondo. Es la vía preferida (paso 3.1 del
               método): no toca el producto. Las unidades se cuentan a ojo.
  componer  -> N copias REALES de la foto de una unidad, juntas, sobre fondo
               blanco, 1600x1600. Para cuando el proveedor no trae una foto con
               las N unidades. No inventa producto: repite la foto real.
  sello     -> sello redondo "3 PACK" en la esquina más tranquila. OJO: la
               política de TikTok Shop US prohíbe texto o gráficos añadidos en
               las fotos de producto; úsalo solo con la decisión de Snailer.

  python tools/pack_foto.py cuadrar --entrada pack4_proveedor.jpg --cantidad 4 --salida principal4.jpg
  python tools/pack_foto.py componer --entrada unidad.jpg --cantidad 3 --salida pack3.jpg
  python tools/pack_foto.py sello --entrada pack3.jpg --cantidad 3 --salida pack3_sello.jpg
  python tools/pack_foto.py lote --plan plan.json

plan.json = [{"orden": "cuadrar"|"componer"|"sello", "entrada": "...", "cantidad": 3,
              "salida": "...", "unidad": "PACK"}, ...]
Cada salida deja al lado un .json con el sha256 de entrada y salida (evidencia).
Código de salida 2 = hay fotos para REVISAR A OJO.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageStat

FUENTES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
LADO_MINIMO = 1600  # Helen'shop: foto principal de 1600 px o más
LADO_SALIDA = 1600
UNIDADES = {"PACK", "PAIRS", "PCS", "SET"}
ESQUINAS = ("tl", "tr", "bl", "br")
UMBRAL_OCUPADA = 18.0  # detalle medio a partir del cual la esquina tapa producto
MAX_UNIDADES_COMPONER = 12  # más de 12 ya no se distinguen: usar foto del proveedor
MAX_AMPLIACION = 1.6  # ampliar más que esto emborrona: pedir una foto mayor al proveedor


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def leer_bytes(origen: str) -> bytes:
    if origen.startswith(("http://", "https://")):
        pedido = urllib.request.Request(origen, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(pedido, timeout=60) as r:
            return r.read()
    return Path(origen).read_bytes()


def fuente(tamano: int) -> ImageFont.FreeTypeFont:
    for ruta in FUENTES:
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, tamano)
    raise SystemExit("No encontré una fuente en negrita: " + ", ".join(FUENTES))


def validar(cantidad: int, unidad: str = "PACK") -> str:
    if cantidad < 2:
        raise SystemExit("Un pack tiene 2 unidades o más; con 1 no se toca la foto.")
    unidad = unidad.upper()
    if unidad not in UNIDADES:
        raise SystemExit(f"Unidad no válida: {unidad}. Usa una de {sorted(UNIDADES)}")
    return unidad


# ---------------------------------------------------------------- fondo
def a_rgb(img: Image.Image) -> Image.Image:
    """RGB sobre blanco: un PNG con fondo transparente no debe salir con fondo negro."""
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        base = Image.new("RGB", rgba.size, (255, 255, 255))
        base.paste(rgba, mask=rgba.getchannel("A"))
        return base
    return img.convert("RGB")


def fondo_de_borde(rgb: Image.Image, tolerancia: int = 28) -> tuple[tuple[int, int, int], float]:
    """Color del fondo (mediana del borde) y fracción del borde que es ese fondo.

    Si la fracción es baja, la foto no tiene fondo liso: recortar o rellenar se nota.
    """
    ancho, alto = rgb.size
    borde = [rgb.getpixel((x, y)) for x in range(0, ancho, max(1, ancho // 50)) for y in (0, alto - 1)]
    borde += [rgb.getpixel((x, y)) for y in range(0, alto, max(1, alto // 50)) for x in (0, ancho - 1)]
    fondo = tuple(sorted(c[i] for c in borde)[len(borde) // 2] for i in range(3))
    claros = sum(1 for c in borde if max(abs(c[i] - fondo[i]) for i in range(3)) <= tolerancia)
    return fondo, claros / len(borde)


# ---------------------------------------------------------------- cuadrar
def cuadrar(img: Image.Image, cantidad: int) -> tuple[Image.Image, dict]:
    """Foto del proveedor con el pack completo -> cuadrada, 1600x1600, mismo fondo.

    Solo añade fondo a los lados y cambia el tamaño: el producto no se toca.
    """
    rgb = a_rgb(img)
    fondo, fraccion_fondo = fondo_de_borde(rgb)
    lado = max(rgb.size)
    lienzo = Image.new("RGB", (lado, lado), fondo)
    lienzo.paste(rgb, ((lado - rgb.width) // 2, (lado - rgb.height) // 2))
    escala = LADO_SALIDA / lado
    if lado != LADO_SALIDA:
        lienzo = lienzo.resize((LADO_SALIDA, LADO_SALIDA), Image.LANCZOS)
    datos = {
        "orden": "cuadrar",
        "unidades_en_foto": f"{cantidad} según la ficha del proveedor: contarlas a ojo",
        "tamano_original": list(rgb.size),
        "escala": round(escala, 3),
        "color_relleno": list(fondo),
        "fondo_liso_en_borde": round(fraccion_fondo, 2),
        "tamano": [LADO_SALIDA, LADO_SALIDA],
        "lado_minimo_ok": True,
        # Relleno sobre fondo no liso se nota; ampliar demasiado emborrona.
        "revisar_a_ojo": fraccion_fondo < 0.8 or escala > MAX_AMPLIACION,
    }
    return lienzo, datos


# ---------------------------------------------------------------- componer
def recortar_unidad(img: Image.Image, tolerancia: int = 28) -> tuple[Image.Image, float]:
    """Recorta la unidad separándola del fondo claro del borde.

    Devuelve la unidad en RGBA y la fracción de borde que era fondo claro
    (si es baja, la foto no tiene fondo liso y el recorte hay que mirarlo).
    """
    rgb = a_rgb(img)
    ancho, alto = rgb.size
    fondo, fraccion_fondo = fondo_de_borde(rgb, tolerancia)
    diferencia = ImageChops.difference(rgb, Image.new("RGB", rgb.size, fondo)).convert("L")
    mascara = diferencia.point(lambda v: 255 if v > tolerancia else 0).filter(ImageFilter.MaxFilter(5))
    mascara = mascara.filter(ImageFilter.GaussianBlur(1.2))
    caja = mascara.getbbox() or (0, 0, ancho, alto)
    unidad = rgb.crop(caja).convert("RGBA")
    unidad.putalpha(mascara.crop(caja))
    return unidad, fraccion_fondo


def rejilla(cantidad: int) -> tuple[int, int]:
    columnas = math.ceil(math.sqrt(cantidad))
    filas = math.ceil(cantidad / columnas)
    return columnas, filas


def componer(img: Image.Image, cantidad: int) -> tuple[Image.Image, dict]:
    if cantidad > MAX_UNIDADES_COMPONER:
        raise SystemExit(f"Más de {MAX_UNIDADES_COMPONER} unidades: usa la foto del proveedor con el pack completo.")
    unidad, fraccion_fondo = recortar_unidad(img)
    columnas, filas = rejilla(cantidad)
    margen = int(LADO_SALIDA * 0.06)
    hueco = int(LADO_SALIDA * 0.03)
    celda_w = (LADO_SALIDA - 2 * margen - (columnas - 1) * hueco) / columnas
    celda_h = (LADO_SALIDA - 2 * margen - (filas - 1) * hueco) / filas
    escala = min(celda_w / unidad.width, celda_h / unidad.height)
    pieza = unidad.resize((max(1, int(unidad.width * escala)), max(1, int(unidad.height * escala))), Image.LANCZOS)
    lienzo = Image.new("RGB", (LADO_SALIDA, LADO_SALIDA), (255, 255, 255))
    alto_bloque = filas * pieza.height + (filas - 1) * hueco
    y = (LADO_SALIDA - alto_bloque) // 2
    colocadas = 0
    for fila in range(filas):
        en_fila = min(columnas, cantidad - colocadas)
        ancho_fila = en_fila * pieza.width + (en_fila - 1) * hueco
        x = (LADO_SALIDA - ancho_fila) // 2
        for _ in range(en_fila):
            lienzo.paste(pieza, (x, y), pieza)
            x += pieza.width + hueco
            colocadas += 1
        y += pieza.height + hueco
    datos = {
        "orden": "componer",
        "unidades_en_foto": colocadas,
        "rejilla": [columnas, filas],
        "escala_unidad": round(escala, 3),
        "fondo_liso_en_borde": round(fraccion_fondo, 2),
        "tamano": [LADO_SALIDA, LADO_SALIDA],
        "lado_minimo_ok": True,
        # Si la foto original no tenía fondo liso, el recorte puede llevarse fondo:
        "revisar_a_ojo": fraccion_fondo < 0.8 or escala > MAX_AMPLIACION,
    }
    return lienzo, datos


# ---------------------------------------------------------------- sello
def caja_esquina(esquina: str, ancho: int, alto: int, diametro: int, margen: int):
    x0 = margen if esquina in ("tl", "bl") else ancho - margen - diametro
    y0 = margen if esquina in ("tl", "tr") else alto - margen - diametro
    return (x0, y0, x0 + diametro, y0 + diametro)


def detalle(img: Image.Image, caja) -> float:
    """Detalle medio de la zona (bordes). Fondo liso ~0; producto o texto >> 0."""
    zona = img.crop(caja).convert("L").filter(ImageFilter.FIND_EDGES)
    return float(ImageStat.Stat(zona).mean[0])


def color_rgb(hexa: str) -> tuple[int, int, int]:
    hexa = hexa.lstrip("#")
    if len(hexa) != 6:
        raise SystemExit(f"Color no válido: #{hexa}")
    return tuple(int(hexa[i:i + 2], 16) for i in (0, 2, 4))


def poner_sello(img: Image.Image, cantidad: int, unidad: str = "PACK", esquina_pedida: str = "auto",
                color: str = "#111111", proporcion: float = 0.22) -> tuple[Image.Image, dict]:
    unidad = validar(cantidad, unidad)
    base = img.convert("RGB")
    ancho, alto = base.size
    corto = min(ancho, alto)
    diametro = max(120, int(corto * proporcion))
    margen = max(12, int(corto * 0.03))
    medidas = {e: detalle(base, caja_esquina(e, ancho, alto, diametro, margen)) for e in ESQUINAS}
    esquina = min(medidas, key=medidas.get) if esquina_pedida == "auto" else esquina_pedida
    x0, y0, _, _ = caja_esquina(esquina, ancho, alto, diametro, margen)

    escala = 4  # se dibuja a 4x y se reduce: bordes suaves
    lado = diametro * escala
    sello = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(sello)
    aro = max(2, int(lado * 0.035))
    d.ellipse((0, 0, lado - 1, lado - 1), fill=(255, 255, 255, 255))
    d.ellipse((aro, aro, lado - 1 - aro, lado - 1 - aro), fill=color_rgb(color) + (255,))
    numero = str(cantidad)
    f_num = fuente(int(lado * (0.46 if len(numero) == 1 else 0.36)))
    f_uni = fuente(int(lado * 0.17))
    d.text((lado / 2, lado * 0.44), numero, font=f_num, fill=(255, 255, 255, 255), anchor="mm")
    d.text((lado / 2, lado * 0.74), unidad, font=f_uni, fill=(255, 255, 255, 255), anchor="mm")
    sello = sello.resize((diametro, diametro), Image.LANCZOS)

    salida = base.copy()
    salida.paste(sello, (x0, y0), sello)
    datos = {
        "orden": "sello",
        "texto_sello": f"{cantidad} {unidad}",
        "esquina": esquina,
        "detalle_por_esquina": {k: round(v, 2) for k, v in medidas.items()},
        "esquina_ocupada": medidas[esquina] > UMBRAL_OCUPADA,
        "tamano": [ancho, alto],
        "lado_minimo_ok": corto >= LADO_MINIMO,
        "diametro_sello_px": diametro,
        "aviso_politica": "TikTok Shop US prohíbe texto o gráficos añadidos en fotos de producto; "
                          "solo con decisión de Snailer.",
    }
    datos["revisar_a_ojo"] = datos["esquina_ocupada"] or not datos["lado_minimo_ok"]
    return salida, datos


# ---------------------------------------------------------------- común
def procesar(orden: str, entrada: str, cantidad: int, salida: str, unidad: str = "PACK",
             esquina: str = "auto", color: str = "#111111") -> dict:
    unidad = validar(cantidad, unidad)
    crudo = leer_bytes(entrada)
    with Image.open(io.BytesIO(crudo)) as img:
        img.load()
        if orden == "cuadrar":
            resultado, datos = cuadrar(img, cantidad)
        elif orden == "componer":
            resultado, datos = componer(img, cantidad)
        elif orden == "sello":
            resultado, datos = poner_sello(img, cantidad, unidad, esquina, color)
        else:
            raise SystemExit(f"Orden desconocida: {orden}")
    destino = Path(salida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    resultado.save(buffer, format="JPEG", quality=92, optimize=True)
    destino.write_bytes(buffer.getvalue())
    datos.update({
        "cantidad": cantidad,
        "unidad": unidad,
        "entrada": entrada,
        "entrada_sha256": sha256(crudo),
        "salida": str(destino),
        "salida_sha256": sha256(buffer.getvalue()),
    })
    destino.with_suffix(".json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    return datos


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("orden", choices=["cuadrar", "componer", "sello", "lote"])
    ap.add_argument("--entrada", help="ruta o URL de la foto")
    ap.add_argument("--cantidad", type=int, help="unidades de ESA variante según la ficha del proveedor")
    ap.add_argument("--salida", help="ruta del JPG resultante")
    ap.add_argument("--unidad", default="PACK", help="PACK, PAIRS, PCS o SET (el listing va en inglés)")
    ap.add_argument("--esquina", default="auto", choices=("auto",) + ESQUINAS)
    ap.add_argument("--color", default="#111111")
    ap.add_argument("--plan", help="JSON con varias fotos (principal + variantes)")
    a = ap.parse_args(argv)

    if a.orden == "lote":
        if not a.plan:
            ap.error("lote necesita --plan")
        trabajos = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    elif a.entrada and a.cantidad and a.salida:
        trabajos = [{"orden": a.orden, "entrada": a.entrada, "cantidad": a.cantidad, "salida": a.salida,
                     "unidad": a.unidad, "esquina": a.esquina, "color": a.color}]
    else:
        ap.error("usa --entrada, --cantidad y --salida")

    revisar = 0
    for t in trabajos:
        datos = procesar(t["orden"], t["entrada"], int(t["cantidad"]), t["salida"], t.get("unidad", "PACK"),
                         t.get("esquina", "auto"), t.get("color", "#111111"))
        aviso = "  <- REVISAR A OJO" if datos["revisar_a_ojo"] else ""
        print(f"{datos['salida']}: {datos['orden']} {datos['cantidad']} {datos['unidad']} "
              f"({datos['tamano'][0]}x{datos['tamano'][1]}){aviso}")
        revisar += bool(datos["revisar_a_ojo"])
    return 2 if revisar else 0


if __name__ == "__main__":
    sys.exit(main())
