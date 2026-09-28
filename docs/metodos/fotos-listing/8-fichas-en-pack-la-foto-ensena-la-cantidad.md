---
type: metodo
cosa: fotos-listing
metodo: 8-fichas-en-pack-la-foto-ensena-la-cantidad
estado: BORRADOR
verificado_el: null
verificado_por: null
dueño: fotos (quien optimice o suba la ficha)
creado: 2026-09-28
creado_por: sesión Claude en la nube, por orden de Snailer
proyectos: [helenshop-mama, roselle-hermana, skaylo]
tags: [fotos, packs, variantes, listing, tiktok-shop, shopify]
---

# FOTOS-LISTING · Método 8 — Fichas en PACK: la foto enseña la cantidad de cada variante

> **Orden de Snailer (28-sep-2026, dictada):** *"las fichas que tengan varios productos en el producto, la imagen principal tiene que traer la cantidad de productos que trae… cuando sean productos en pack, la imagen principal y las variantes tienen que tener la cantidad que viene en el pack correspondiente a la variante y el producto."*
> Corrige el prompt oficial de optimización de fichas, que no lo decía. Aplica a **toda ficha nueva y a toda ficha ya optimizada**.

## 0. Para qué sirve y cuándo usar ESTE y no otro
- **Resultado:** en una ficha que vende más de una unidad, la **foto principal** enseña todas las unidades del pack, y la **foto de cada variante** enseña las unidades de **esa** variante. El título y el nombre de cada variante dicen la cantidad. Queda un JSON por foto con el sha256 de antes y después.
- **Úsalo cuando:** la ficha del proveedor vende 2 o más unidades (pack, set, pares, piezas) o hay variantes por cantidad (1 / 2 / 3 unidades).
- **NO lo uses cuando:** se vende 1 unidad. Para arreglar una foto fea usa `metodos-fotos-listing-6-optimizar-foto-el-motor-mas-rapido`; para infografías con texto, `metodos-fotos-listing-5-infografia-overlay-pil`.
- **Coste:** 0 $ (Pillow local). Tiempo típico: 1-3 min por ficha, más la relectura de la tienda.

## 1. Prerrequisitos (comprobables ANTES de empezar)
- [ ] **Ficha del proveedor con la cantidad por variante** y su enlace (CJ: nombre de variante y lista de empaque; Amazon: "Number of Items", "Unit Count" o "Pack of N"). **Lo que se vende lo define la ficha del proveedor, nunca la foto** (regla de la hielera).
- [ ] ID exacto del producto en la tienda (TikTok o Shopify) y su ruta: Helen'shop = API de TikTok de Helen'shop; Roselle = API de Roselle (desde 26-sep, `metodos-roselle-optimizar-ficha-por-api`) o la app de TikTok dentro de Shopify Skaylo; Skaylo = Shopify.
- [ ] Fotos reales del proveedor. Para componer hace falta **una foto de una unidad sobre fondo liso**.
- [ ] `python tools/pack_foto.py --help` responde (repo de la nube `snailer9811work-design/Test-`).

## 2. Pasos
1. **Tabla de cantidades.** Por cada variante: nombre, cantidad, fuente (enlace a la ficha del proveedor). Si la ficha no dice la cantidad → la variante queda **DESCONOCIDA con razón**; no se adivina por la foto.
2. **Título y variantes.** El título lleva la cantidad en inglés ("3-Pack", "Pack of 3", "2 Pairs", "Set of 4"). Si las variantes tienen cantidades distintas, cada nombre de variante la lleva ("Black, 3-Pack"). Política de TikTok Shop US: *"For multi-pack products, or products that contain more than a single item, quantity should be clearly stated (for example, '10 ct' or 'Pack of 10')"*.
3. **Foto principal = las N unidades a la vista.** Orden de preferencia:
   1. foto real del proveedor que ya enseña el pack completo. Mira primero la galería de la propia ficha: a veces ya está y basta con pasarla al puesto 1. Para dejarla cuadrada a 1600×1600 sin tocar el producto: `python tools/pack_foto.py cuadrar --entrada <foto del pack> --cantidad N --salida principal_N.jpg`;
   2. si no existe: `python tools/pack_foto.py componer --entrada <foto de 1 unidad> --cantidad N --salida principal_N.jpg` (repite la foto real N veces sobre blanco, 1600×1600; no inventa producto);
   3. si la foto de la unidad no tiene fondo liso (la herramienta sale con código 2 y "REVISAR A OJO"): generar con el motor vigente (`fotos-listing-1` o `-6`) con PRODUCT LOCK y el número exacto de unidades en el prompt, y comprobar la fidelidad a ojo.
4. **Foto de cada variante.** Cada variante lleva su propia foto con **su** cantidad (la de 2 enseña 2; la de 4 enseña 4). Si el eje de variante es el color dentro de un pack fijo (3-pack negro / 3-pack beige), cada color enseña sus 3 unidades de ese color.
5. **Sello "N PACK" (solo con decisión de Snailer).** La política de TikTok Shop US dice: *"All product images must not include any added logos, text, borders, watermarks, or graphics covering the product or in the background."* Por eso el sello **no** es obligatorio. Si Snailer lo aprueba: `python tools/pack_foto.py sello --entrada principal_N.jpg --cantidad N --salida principal_N_sello.jpg` (círculo pequeño en la esquina más limpia; nunca una banda de texto; el sello y el listing van en inglés).
6. **Subir por la ruta de la tienda, sobre el MISMO ID.** Nunca crear otro producto. No tocar precio ni stock. Roselle: `skus[]` siempre con `id` + `seller_sku` y el guard `check_partial_edit_skus.py`. Guardar la foto y la ficha de antes.
7. **Releer la tienda** (TikTok: `return_under_review_version=true`) y comprobar la foto principal y la de cada variante. Esperar la auditoría de TikTok: PENDING no es APPROVED.

## 3. Gate / QA (qué se mide antes de decir HECHO)
- [ ] Tabla de cantidades con el enlace del proveedor en cada fila.
- [ ] La foto principal enseña exactamente N unidades (contadas a ojo).
- [ ] Cada variante tiene su foto y enseña su cantidad; ninguna variante reutiliza la foto de otra cantidad.
- [ ] Título y nombres de variante dicen la cantidad, en inglés.
- [ ] Ninguna foto promete más unidades, accesorios o productos de los que se venden.
- [ ] Helen'shop: foto principal de 1600 px o más (`lado_minimo_ok: true` en el JSON).
- [ ] Sin sello salvo decisión de Snailer; nunca una banda de texto.
- [ ] Relectura de la tienda hecha: ID, foto principal, foto por variante y estado de auditoría.
- [ ] Precio y stock sin cambios (antes = después).

## 4. Errores conocidos y cómo se ven
- 2026-09-28 — Ficha "licra de mármol" optimizada con el prompt oficial sin la regla de packs: la foto principal y las variantes no enseñaban la cantidad del pack → **origen de este método**. Hay que rehacerla con los pasos 1-7.
  Era un pack de 4 shorts tie-dye de Skaylo. La principal enseñaba 1 short puesto (foto de modelo) y 5 de 25 combinaciones no tenían foto propia. La foto del proveedor con los 4 ya estaba en la galería (puesto 2). Detalle privado en Drive: `CENTRO_DE_MANDO/skaylo-packs-foto-principal-2026-09-28.md`.
- Foto de modelo con 1 unidad puesta como principal de un pack: queda bonita, pero vende 1. Va en la galería, nunca en el puesto 1.
- Variantes de color dentro de un pack (Black 4-Pack / Pastel 4-Pack) sin foto propia: el comprador que elige otra combinación ve la foto de la primera. Cada combinación lleva su foto con sus N unidades.
- La foto de marketing del proveedor enseña más unidades o accesorios de los que se venden → la cantidad sale de la ficha, nunca de la foto.
- Foto de una unidad con fondo de escena (gimnasio, modelo) → `componer` no la recorta bien y avisa con código 2. Usar la foto del pack del proveedor o el motor con PRODUCT LOCK.
- Sello en español en un listing en inglés, o sello tapando el producto → usar inglés y la esquina que elige la herramienta; si todas las esquinas están ocupadas, no poner sello.

## 5. Fuentes
- Orden de Snailer, 28-sep-2026 (texto al principio de esta página).
- TikTok Shop US — Product Listing Policy: https://seller-us.tiktok.com/university/essay?knowledge_id=3196690250417921&default_language=en (leída el 28-sep-2026: cantidad clara en packs; sin texto ni gráficos añadidos en las fotos; la foto principal representa de forma objetiva lo que se vende).
- Regla de la hielera (`playbooks/regla-de-la-hielera-ficha-manda`) y `SecondBrain/REGLA_PRODUCTOS_SIEMPRE_CON_LINK.md`: la foto sirve para saber QUÉ ES; la ficha para saber QUÉ SE VENDE.
- `metodos-sourcing-10-packs-cantidad-antes-que-diseno` (packs a listar) y `metodos-fotos-listing-5-infografia-overlay-pil` (texto con Pillow, nunca pedido al generador).
- Herramienta: `tools/pack_foto.py` en el repo `snailer9811work-design/Test-` (8 pruebas).

## 6. Historial de cambios
- 2026-09-28 Claude (nube) — Creado por orden de Snailer. BORRADOR hasta que alguien lo siga de punta a punta en una ficha real y la relea en la tienda.
- 2026-09-28 Claude (nube) — Paso 3.1: mirar primero la galería de la ficha y orden `cuadrar` (foto del proveedor a 1600×1600 sin tocar el producto). Añadidos dos errores conocidos, vistos al auditar las 54 fichas en pack de Skaylo.
