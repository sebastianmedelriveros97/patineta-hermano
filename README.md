# Patineta hermano + kit trote para Maxi-Cosi Leona 2

Accesorios imprimibles en 3D, paramétricos y **de enganche rápido** para el coche **Maxi-Cosi Leona 2**.

📘 **[Manual de armado y materiales (PDF)](docs/manual_armado.pdf)**: materiales a comprar, piezas, pasos y revisión, separados por sistema.
📐 **[Plano general 1:10 (A3)](docs/plano_general.svg)**

![plano general](docs/plano_general.png)

| Sistema | Qué hace | Poner / sacar | STL |
|---|---|---|---|
| **1. Kit trote** | 3 ruedas **EVA 12" macizas** (sin cámara, livianas). Dos módulos de ruedas que se **enclachan** en 4 soportes fijos. | ≈ 1 min · 4 pasadores de bola | `stl/01_kit_running` |
| **2. Patineta hermano** | Tabla con sillín detrás del coche. **Rebatible**: se levanta, queda colgada atrás y se fija con una hebilla. | ≈ 20 s · 2 pasadores · plegar ≈ 5 s | `stl/02_patineta` |
| **3. Hamaca** | Lona para que la niña duerma sentada en el sillín, mirando hacia el adulto. | ≈ 30 s · 4 hebillas click | `stl/03_hamaca` |
| **4. Bandeja** | Bandeja para tablet de 11", con 2 portavasos y calzos, sobre el manillar, a los lados del botón de plegado. | ≈ 20 s · 4 perillas | `stl/04_bandeja` |

> ⚠️ Esto es una modificación casera: Maxi-Cosi no la aprueba y anula la garantía. Antes de subir a los niños, prueba todo con 20 kg de arena.
> Para trotar: usa siempre la correa de muñeca y saca la patineta y la hamaca. Lee la página de seguridad del manual.

## Cómo funciona el enganche rápido
- **En el coche quedan fijas** solo abrazaderas pequeñas, que no impiden plegarlo:
  - 4 soportes con "silla" en U (kit trote);
  - 2 abrazaderas pivote (patineta);
  - 2 anclajes (hamaca);
  - 2 abrazaderas (bandeja).
- **Módulo delantero:** travesaño 20x20 + horquilla de 2 pletinas + 1 rueda EVA. **Módulo trasero:** travesaño 20x20 + 2 horquillas + 2 ruedas EVA.
  - Cada módulo entra en sus sillas y se traba con **pasadores de bola**: aprietas el botón, metes el pasador, sueltas y queda trabado.
  - El coche sube ~5 cm y las ruedas originales quedan en el aire. Las ruedas traseras originales van juntas al centro, así que las nuevas van por fuera de las patas: trocha 58 cm, ancho total ≈ 69 cm.
  - Freno de estacionamiento: un pasador entre los rayos de la rueda EVA trasera.
- **Patineta:** los brazos se unen a las orejas de las abrazaderas pivote con 2 pasadores de bola Ø8. Para rebatirla, se levanta hasta que la tabla cuelga detrás del coche y se abrocha una hebilla de seguridad.
- Cada rueda va sujeta por los **dos lados** (horquilla) y el esfuerzo lo toma el acero. Por eso sirve el eje roscado M8/M10 típico de las ruedas EVA de bicicleta de equilibrio.

## Ruedas EVA aro 12"
Busca en Mercado Libre o Falabella: *«rueda EVA 12 pulgadas»*, *«rueda repuesto bicicleta de equilibrio aro 12»*, *«rueda maciza aro 12 bicicleta niño»*. Antes de comprar, pregúntale al vendedor:
- el diámetro exterior (≈ 29–30 cm);
- el **ancho del buje entre tuercas**;
- la **medida del eje** (M8 o M10).

Con esas medidas, ajusta `RUEDA_RUNNING_DIAM`, `BUJE_ANCHO` y `EJE_RUEDA` en `cad/params.py`.

Las ruedas EVA no se pinchan, pero amortiguan menos que un neumático con aire. Son para pavimento, ciclovía o tierra compactada, a ritmo moderado.

## Antes de imprimir: medir y regenerar
La geometría está calibrada con fotos del Leona 2: chasis en X, ruedas traseras juntas con resortes y freno central, y manillar en asa con el botón de plegado al centro. Confirma con huincha las que dicen `[MEDIR]`, imprime `stl/00_pruebas` y regenera todo:

```bash
pip install manifold3d trimesh numpy networkx scipy matplotlib
python3 cad/build.py      # STL + docs/lista_piezas_impresas.md + docs/cortes_metal.md + plantillas 1:1
python3 cad/plano.py      # docs/plano_general.svg
python3 cad/thumbs.py     # miniaturas para el manual
python3 cad/manual.py     # docs/manual_armado.pdf (usa Chromium/Playwright)
```
`build.py` avisa si algo choca, por ejemplo si el travesaño trasero roza la rueda original.

## Estructura
```
cad/params.py   ← todas las medidas (edita aquí)
cad/geom.py     ← geometría del coche y posiciones de cada módulo
cad/parts.py    ← geometría de cada pieza (Python + manifold3d)
cad/build.py    ← STL, cortes de metal y plantillas
cad/plano.py    ← plano general 1:10
cad/manual.py   ← manual PDF
stl/            ← STL listos para laminar
docs/           ← manual PDF, plano, plantillas 1:1 de pletinas, cortes, lista de piezas
```
