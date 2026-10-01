# CANDIDATOS · Tanda 1 · 2026-10-01 · DEMANDA (Helen'shop, por VÍDEO)

**ESTADO: INCOMPLETO. 0 de 5 candidatos verificados.** Sin enlace de vídeo, ventas ni SKU/stock/coste de CJ comprobados, no hay fila válida. Por regla ("cero números inventados") no relleno nada.

## Qué probé (fuentes en orden) y qué salió
| Fuente | Resultado |
|---|---|
| Drive SecondBrain `helenshop-mama.md` y `15-reto-14-dias…` | Leídos (fragmento). Confirman: cupo 3 productos por VÍDEO, shop id 7496047698683398459, CJ cuenta CJ4793403 con tienda `tiktok_us`, API de demanda (`data.bestselling.public.read`, `tt_oportunidades.py`) **en el PC de Snailer**, no accesible desde la nube. Ningún archivo de Drive trae lista de productos ganadores. |
| App flowhelen-panel.fly.dev/mama | Pide usuario y contraseña. **Sin acceso.** |
| FastMoss (ranking de ventas) | La página carga vacía ("No data"): hay que iniciar sesión. |
| CJ web (búsqueda almacén US) | Redirige a verificación anti-robot. **Bloqueado.** |
| CJ API (`developers.cjdropshipping.com`) | HTTP 401: necesita el token de CJ4793403 (vive en el PC de Snailer). |
| TikTok Shop / Creative Center | Páginas dinámicas, sin datos legibles sin sesión. |
| Blogs de tendencias (búsqueda web) | Solo categorías, **sin ventas, sin fecha por producto, sin enlaces**: no valen como "señal de ventas". |

## Lo único comprobado: pistas de categoría para octubre (NO son candidatos)
Fuente: [Delzonic](https://delzonic.com/blogs/tiktok-shop-halloween-products-2026/) y [astools](https://news.astools.app/en/blog/tiktok-viral-products-october-2026) (artículos de blog, sin cifras por producto).
- Halloween: accesorios de disfraz (menos riesgo de talla), decoración que luce en cámara en cuarto oscuro, maquillaje/efectos. El pico de venta termina hacia el **24-26 oct** (corte de entrega); hoy es 1-oct → ventana real ≈ 3 semanas.
- Otoño/hogar acogedor y regalos tempranos (11.11).

**Búsquedas a ejecutar en CJ (filtro almacén EE. UU.) y en FastMoss/Kalodata — todo SIN COMPROBAR:**
1. Luces LED / proyector de Halloween · 2. Accesorios de disfraz LED · 3. Decoración tipo calabaza/telaraña con luz · 4. Calentador/manta eléctrica o gadget de frío · 5. Gadget de cocina de otoño con demostración.
Para cada uno falta: vídeo ganador con fecha, unidades vendidas con fecha, SKU CJ con stock US, coste y flete.

## Plantilla de fila (para completar cuando haya datos)
| # | Producto | Vídeo TikTok (enlace+fecha) | Producto TikTok (enlace) | Ventas con fecha | CJ enlace/SKU/stock US | Coste+flete | Escalera v2 | ×3 | Mínimo (coste+flete)/(1−comisión) | Margen real | CJ US / Ali / Alibaba / Amazon |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-5 | sin comprobar | sin comprobar | sin comprobar | sin comprobar | sin comprobar | sin comprobar | sin comprobar | sin comprobar | comisión TikTok: sin comprobar (no la invento) | sin comprobar | sin comprobar |

Escalera v2 (de las reglas): coste total ≤10 → +5,99 · ≤15 → +7,99 · ≤20 → +9,99 · ≤25 → +14,99 · ≤30 → +19,99. Para ganar ≥ $8 netos, mirar productos de coste ≤15 con +7,99 solo si la comisión deja ≥ $8; **con la comisión sin comprobar no puedo afirmarlo**.

## OPORTUNIDADES DE NEGOCIO (sin cifras comprobadas)
| Idea | Qué haría | Coste/ganancia/riesgo |
|---|---|---|
| Paquete 2×1 de Halloween (luz + accesorio) | Sube el ticket por encima del umbral de $8 | Necesita costes reales de CJ: sin comprobar. Riesgo: el corte del 24-26 oct. |
| Nicho de baja competencia en vídeo | Elegir el producto con pocos vídeos y ventas ya visibles | Necesita FastMoss/Kalodata con sesión: sin comprobar. |
| Priorizar los 3 huecos del cupo (vídeo) con lo que ya devuelve `tt_oportunidades.py` | Es la fuente validada por Snailer el 12-sep | Se ejecuta en su PC; coste $0. |

## BLOQUEO y qué hace falta (solo Snailer puede)
1. **Correr en su PC** `tt_oportunidades.py` / "Buscar demanda" y pegarme la salida (o dejar el CSV en Drive), o darme sesión en FastMoss/Kalodata.
2. **Token de CJ** (o exportar a Drive búsquedas con almacén US) para SKU, stock y flete.
3. Con eso cierro las 5 filas en una tanda corta.
