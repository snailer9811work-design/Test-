import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import pack_foto  # noqa: E402


def foto_unidad(ruta: Path, lado: int = 1000) -> None:
    """Una 'unidad' oscura centrada sobre fondo blanco, como la foto de un proveedor."""
    img = Image.new("RGB", (lado, lado), (255, 255, 255))
    ImageDraw.Draw(img).rounded_rectangle((300, 250, 700, 750), radius=40, fill=(30, 30, 30))
    img.save(ruta)


def foto_con_producto_arriba_izquierda(ruta: Path, lado: int = 1600) -> None:
    img = Image.new("RGB", (lado, lado), (245, 245, 245))
    d = ImageDraw.Draw(img)
    for x in range(0, lado // 2, 12):
        d.line((x, 0, x, lado // 2), fill=(20, 20, 20), width=5)
    img.save(ruta)


def contar_manchas_oscuras(img: Image.Image) -> int:
    """Cuenta bloques oscuros separados en una fila/columna central de muestreo."""
    gris = img.convert("L")
    ancho, alto = gris.size
    visto = set()
    manchas = 0
    for y in range(0, alto, 20):
        for x in range(0, ancho, 20):
            if gris.getpixel((x, y)) < 80 and (x // 20, y // 20) not in visto:
                manchas += 1
                pila = [(x // 20, y // 20)]
                while pila:
                    cx, cy = pila.pop()
                    if (cx, cy) in visto or not (0 <= cx * 20 < ancho and 0 <= cy * 20 < alto):
                        continue
                    if gris.getpixel((cx * 20, cy * 20)) >= 80:
                        continue
                    visto.add((cx, cy))
                    pila += [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
    return manchas


class ComponerTest(unittest.TestCase):
    def test_tres_unidades_reales_en_1600(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada = Path(tmp) / "unidad.png"
            foto_unidad(entrada)
            datos = pack_foto.procesar("componer", str(entrada), 3, str(Path(tmp) / "pack3.jpg"))
            self.assertEqual(datos["unidades_en_foto"], 3)
            self.assertEqual(datos["tamano"], [1600, 1600])
            self.assertFalse(datos["revisar_a_ojo"])
            with Image.open(datos["salida"]) as im:
                self.assertEqual(im.size, (1600, 1600))
                self.assertEqual(contar_manchas_oscuras(im), 3)

    def test_demasiadas_unidades_se_niega(self):
        with self.assertRaises(SystemExit):
            pack_foto.componer(Image.new("RGB", (400, 400), "white"), 20)


class SelloTest(unittest.TestCase):
    def test_sello_en_esquina_libre_con_evidencia(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada = Path(tmp) / "foto.png"
            foto_con_producto_arriba_izquierda(entrada)
            datos = pack_foto.procesar("sello", str(entrada), 3, str(Path(tmp) / "out" / "foto_3pack.jpg"))
            self.assertNotEqual(datos["esquina"], "tl")
            self.assertEqual(datos["texto_sello"], "3 PACK")
            self.assertTrue(datos["lado_minimo_ok"])
            self.assertIn("TikTok", datos["aviso_politica"])
            salida = Path(datos["salida"])
            with Image.open(salida) as im:
                self.assertEqual(im.size, (1600, 1600))
            manifiesto = json.loads(salida.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifiesto["salida_sha256"]), 64)
            self.assertNotEqual(manifiesto["entrada_sha256"], manifiesto["salida_sha256"])

    def test_foto_pequena_pide_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada = Path(tmp) / "chica.png"
            foto_con_producto_arriba_izquierda(entrada, lado=800)
            datos = pack_foto.procesar("sello", str(entrada), 2, str(Path(tmp) / "chica_2.jpg"), unidad="PAIRS")
            self.assertFalse(datos["lado_minimo_ok"])
            self.assertTrue(datos["revisar_a_ojo"])
            self.assertEqual(datos["texto_sello"], "2 PAIRS")

    def test_una_unidad_no_es_pack(self):
        with self.assertRaises(SystemExit):
            pack_foto.validar(1)


if __name__ == "__main__":
    unittest.main()
