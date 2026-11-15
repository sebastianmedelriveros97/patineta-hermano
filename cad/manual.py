"""Genera docs/manual_armado.pdf (y .html): manual de armado y materiales por sistema.
Uso:  python3 cad/manual.py     (requiere haber corrido build.py, plano.py y thumbs.py)"""
import base64
import datetime
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import build as B
import geom as G
import params as P

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS = os.path.join(ROOT, "docs")
C = B.cortes()
fd, ft = C["delantera"], C["trasera"]


def img(name):
    p = os.path.join(DOCS, "img", "piezas", name + ".png")
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()


PLANO = open(os.path.join(DOCS, "plano_general.svg")).read()


def plano_crop(x, y, w, h, width_mm):
    s = re.sub(r'width="420mm" height="297mm" viewBox="0 0 420 297"',
               f'width="{width_mm}mm" height="{width_mm * h / w:.1f}mm" viewBox="{x} {y} {w} {h}"', PLANO, count=1)
    # ids únicos por recorte (markers / patterns)
    tag = f"c{x}_{y}".replace(".", "")
    s = s.replace('id="ar"', f'id="ar{tag}"').replace("url(#ar)", f"url(#ar{tag})")
    s = s.replace('id="mesh"', f'id="mesh{tag}"').replace("url(#mesh)", f"url(#mesh{tag})")
    return f'<div class="plano">{s}</div>'


def piezas_tabla(carpeta):
    rows = []
    for c, nombre, cant, mat, _ in B.PIEZAS:
        if c != carpeta:
            continue
        rows.append(f'<tr><td class="th"><img src="{img(nombre)}"></td><td><code>{nombre}.stl</code></td>'
                    f'<td class="n">{cant}</td><td>{mat}</td></tr>')
    return ('<table class="piezas"><tr><th></th><th>Archivo</th><th>Cant.</th><th>Material / relleno</th></tr>'
            + "".join(rows) + "</table>")


def compras(items):
    rows = "".join(f"<tr><td>{a}</td><td class='n'>{b}</td><td>{c}</td></tr>" for a, b, c in items)
    return f'<table class="compras"><tr><th>Material</th><th>Cant.</th><th>Dónde / nota</th></tr>{rows}</table>'


def pasos(lst):
    return "<ol class='pasos'>" + "".join(f"<li>{x}</li>" for x in lst) + "</ol>"


def check(lst):
    return "<ul class='check'>" + "".join(f"<li>{x}</li>" for x in lst) + "</ul>"


HOY = datetime.date.today().strftime("%d-%m-%Y")

CSS = """
@page { size: A4; margin: 14mm 14mm 16mm 14mm;
  @bottom-center { content: counter(page); font-size: 9pt; color: #888; } }
@page plano { size: A3 landscape; margin: 0; }
body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 10pt; color: #222; line-height: 1.4; }
h1 { font-size: 26pt; margin: 0 0 4mm; }
h2 { font-size: 17pt; margin: 0 0 3mm; padding: 2mm 3mm; color: white; border-radius: 2mm; }
h3 { font-size: 12pt; margin: 5mm 0 2mm; border-bottom: 0.4mm solid #ddd; padding-bottom: 1mm; }
.s1 h2 { background: #e65100; } .s2 h2 { background: #1565c0; } .s3 h2 { background: #2e7d32; } .s4 h2 { background: #6a1b9a; }
.s0 h2 { background: #37474f; }
section { page-break-before: always; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0; font-size: 9pt; }
th, td { border-bottom: 0.2mm solid #ddd; padding: 1.2mm 1.5mm; text-align: left; vertical-align: middle; }
th { background: #f2f2f2; }
td.n { text-align: center; font-weight: bold; white-space: nowrap; }
table.piezas td.th { width: 12mm; padding: 0.2mm; } table.piezas img { width: 11mm; height: 11mm; display: block; } table.piezas td { padding: 0.4mm 1.5mm; }
table.piezas tr { page-break-inside: avoid; }
code { font-size: 8.5pt; background: #f5f5f5; padding: 0 1mm; border-radius: 1mm; }
ol.pasos li { margin-bottom: 1.4mm; } ol.pasos { padding-left: 6mm; }
ul.check { list-style: none; padding-left: 1mm; } ul.check li::before { content: "☐  "; font-size: 11pt; }
.rapido { border: 0.6mm solid #c62828; border-radius: 2mm; padding: 2mm 4mm; margin: 3mm 0; background: #fff5f5; page-break-inside: avoid; }
.rapido h3 { border: none; color: #c62828; margin-top: 1mm; }
.nota { background: #fff8e1; border-left: 1.2mm solid #ffb300; padding: 2mm 3mm; margin: 2mm 0; font-size: 9pt; page-break-inside: avoid; }
.peligro { background: #ffebee; border-left: 1.2mm solid #c62828; padding: 2mm 3mm; margin: 2mm 0; font-size: 9pt; page-break-inside: avoid; }
.plano { text-align: center; margin: 2mm 0; page-break-inside: avoid; }
.cols { display: flex; gap: 6mm; } .cols > div { flex: 1; }
.portada { text-align: center; padding-top: 10mm; }
.portada .sub { font-size: 13pt; color: #555; }
.resumen td:first-child { font-weight: bold; }
.anexo { page: plano; page-break-before: always; }
.anexo svg { width: 420mm; height: 297mm; display: block; }
.tag { display: inline-block; padding: 0.3mm 2mm; border-radius: 1mm; color: white; font-size: 8.5pt; font-weight: bold; }
"""

ruedas_busqueda = ("Mercado Libre / Falabella: <i>«rueda EVA 12 pulgadas»</i>, <i>«rueda repuesto bicicleta de equilibrio aro 12»</i>, "
                   "<i>«rueda maciza aro 12 bicicleta niño»</i>. Pide al vendedor: diámetro exterior, ancho del buje entre tuercas y medida del eje.")

html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Manual de armado</title><style>{CSS}</style></head><body>

<div class="portada s0">
<h1>Manual de armado y materiales</h1>
<p class="sub">Patineta hermano · Kit trote 3 ruedas · Hamaca · Bandeja<br>para coche <b>Maxi-Cosi Leona 2</b></p>
{plano_crop(5, 5, 410, 160, 182)}
<table class="resumen">
<tr><th>Sistema</th><th>Qué hace</th><th>Poner / sacar</th></tr>
<tr><td><span class="tag" style="background:#e65100">1</span> Kit trote</td><td>3 ruedas EVA 12" macizas (sin cámara). Dos módulos de ruedas que se enclachan en 4 soportes fijos.</td><td><b>≈ 1 min</b> · 4 pasadores de bola</td></tr>
<tr><td><span class="tag" style="background:#1565c0">2</span> Patineta</td><td>Tabla con sillín detrás del coche. Rebatible: se levanta y queda colgada atrás.</td><td><b>≈ 20 s</b> · 2 pasadores · plegar: 1 hebilla</td></tr>
<tr><td><span class="tag" style="background:#2e7d32">3</span> Hamaca</td><td>Lona para que la niña duerma sentada en el sillín.</td><td><b>≈ 30 s</b> · 4 hebillas click</td></tr>
<tr><td><span class="tag" style="background:#6a1b9a">4</span> Bandeja</td><td>Tablet 11" + 2 portavasos sobre el manillar.</td><td>Queda puesta (4 pernos)</td></tr>
</table>
<p class="nota">Las medidas del coche son <b>estimadas</b> de la ficha técnica (85,5 × 47 × 103,5 cm; ruedas 18/21 cm). Antes de imprimir, mide tu coche,
corrige <code>cad/params.py</code> y regenera todo (<code>build.py</code> → <code>plano.py</code> → <code>thumbs.py</code> → <code>manual.py</code>): este manual se recalcula solo.
Versión generada el {HOY}.</p>
</div>

<section class="s0">
<h2>0 · Antes de empezar</h2>
<h3>Idea general: lo fijo y lo que se enclacha</h3>
<p>Todo lo que va <b>atornillado al coche</b> son abrazaderas pequeñas que se quedan siempre puestas y no estorban para plegarlo:
4 soportes con silla (kit trote), 2 abrazaderas pivote (patineta), 2 anclajes (hamaca) y 2 abrazaderas de bandeja.
Los módulos grandes (<b>ruedas y patineta</b>) se ponen y sacan con <b>pasadores de bola</b>: aprietas el botón, metes el pasador y queda trabado, sin herramientas.</p>
<h3>Herramientas</h3>
<p>Taladro + brocas 4 / 5 / 6,5 / 8,5 / 10,5 mm · sierra para metal · lima · llaves 8, 10, 13, 17 mm · llave Allen · pie de metro · huincha · tijeras · máquina de coser (hamaca).</p>
<h3>Impresión</h3>
<table><tr><th>Uso</th><th>Material</th><th>Paredes</th><th>Relleno</th></tr>
<tr><td>Soportes, abrazaderas, bloques de horquilla, pivote, yugo</td><td><b>PETG o ASA</b> (nunca PLA)</td><td>6</td><td>100 % (tapas 60 %)</td></tr>
<tr><td>Baldosas de la tabla</td><td>PETG</td><td>4</td><td>40 % giroide</td></tr>
<tr><td>Bandeja, portavasos, sillín</td><td>PETG</td><td>3</td><td>25–30 %</td></tr>
<tr><td>Calzos, tapones</td><td>TPU 95A</td><td>3</td><td>20 %</td></tr></table>
<p>Las piezas ya vienen orientadas; las tuercas van <b>cautivas</b> en alojamientos hexagonales. Imprime primero <code>stl/00_pruebas</code> y verifica que entren
en tu tubo con ~1 mm de juego por lado (ese juego lo rellena una tira de cámara de bicicleta).</p>
<h3>Medidas a tomar del coche</h3>
{check(["Pata trasera y delantera: ancho, fondo, radio de esquina e inclinación",
        "Altura del tope de la carcasa de la rueda trasera y del giratorio delantero",
        "Distancia entre ejes original y distancia del centro a la cara exterior de la rueda trasera",
        "Diámetro del manillar (con espuma) y de los tubos laterales del manillar"])}
<h3>Regla de oro al apretar</h3>
<p>Una vuelta de cámara de bicicleta alrededor del tubo · tuerca en su alojamiento · pernos <b>en cruz</b> hasta que la pieza no gire con la mano. No más: el plástico se parte.</p>
</section>

<section class="s1">
<h2>1 · Kit trote — 3 ruedas EVA 12"</h2>
{plano_crop(5, 25, 200, 135, 182)}
<h3>Materiales a comprar</h3>
{compras([
 ("Rueda EVA aro 12\" (espuma maciza, sin cámara) con rodamientos y eje roscado M10 (o M8)", "3", ruedas_busqueda),
 ("Pasador de bola con botón (quick release pin) Ø6 mm, largo útil 40 mm, inoxidable, con cordón", "4", "Mercado Libre: «pasador bloqueo bola 6 mm» / «quick release pin 6mm». Ver nota sobre largo."),
 ("Tubo cuadrado aluminio 20x20x2 mm", f"{C['trav_del']:.0f} + {C['trav_tras']:.0f} mm", "Sodimac / Easy (tira de 1 m x 2, o 3 m)"),
 ("Pletina acero 30x5 mm", f"2 x {fd['largo']:.0f} + 4 x {ft['largo']:.0f} mm", "Sodimac (≈1,5 m). Pintar con anticorrosivo"),
 ("Perno M6x50 + tuerca + golilla", "20", "soportes con silla (fijos)"),
 ("Perno M6x100 + tuerca autoblocante", "6", "pletinas a bloques de horquilla"),
 ("Perno M6x45 + tuerca autoblocante", "3", "bloque de horquilla al travesaño"),
 ("Golilla M10 (o M8 según rueda)", "6", "entre pletina y tuercas del eje"),
 ("Cámara de bicicleta vieja", "1", "tiras de goma para las abrazaderas"),
 ("Correa de muñeca con mosquetón", "1", "obligatoria para trotar"),
])}
<p class="nota"><b>Largo del pasador:</b> mide la silla impresa ya armada (≈ 36 mm de pared a pared). El largo útil del pasador debe ser 2–6 mm mayor.
Ata cada pasador con su cordón al soporte para no perderlo.</p>
<h3>Piezas impresas</h3>
{piezas_tabla("01_kit_running")}

<h3>A · Preparación (se hace una sola vez)</h3>
{pasos([
 f"Corta los tubos: travesaño delantero <b>{C['trav_del']:.0f} mm</b> y trasero <b>{C['trav_tras']:.0f} mm</b>. Pon los <code>tapon_tubo_cuadrado</code>.",
 "Imprime al 100 % las plantillas <code>plantilla_pletina_horquilla_delantera_1a1.svg</code> (2 pletinas) y <code>…_trasera_1a1.svg</code> (4 pletinas). Comprueba la regla de 100 mm.",
 f"Corta y perfora las pletinas (Ø6,5 / Ø6,5 / Ø{P.EJE_RUEDA + 0.5:.1f}). En <b>una</b> pletina de cada horquilla haz el agujero del eje como <b>ranura de 16 mm</b> para alinear. Pinta.",
 "<b>Módulo delantero:</b> mete el <code>bloque_horquilla_delantera</code> al centro del travesaño, con la punta hacia adelante-abajo. Perfora el tubo a través del bloque (Ø6,5) y fija con M6x45. "
 "Arma pletina – bloque – pletina con 2 x M6x100. Monta la rueda: eje entre las pletinas, golilla y tuerca a cada lado.",
 f"<b>Módulo trasero:</b> igual, con 2 <code>bloque_horquilla_trasera</code>, cada uno centrado a <b>{G.REAR_WHEEL_Y:.0f} mm</b> del centro del travesaño, puntas hacia atrás-abajo. 4 pletinas y 2 ruedas.",
 "Instala los <b>4 soportes con silla</b> (parte A + tapa B, 4–6 x M6x50): sobre las patas, apoyando la cara inferior en la carcasa de la rueda original (tope). "
 "La boca de la U mira <b>hacia adelante</b> en las patas delanteras y <b>hacia atrás</b> en las traseras. Estos soportes quedan siempre puestos.",
 "Presenta cada módulo en sus sillas y perfora el tubo (Ø6,5) usando el agujero de la silla como guía. Así los pasadores siempre calzan.",
 "<b>Alinear:</b> empuja el coche suelto 10 m en plano. Si se desvía, suelta la tuerca del lado ranurado de la rueda delantera, corre el eje 1–2 mm y repite.",
])}

<div class="rapido"><h3>⚡ B · Enclachar (≈ 1 minuto)</h3>
{pasos([
 "Inclina el coche hacia atrás. Mete el travesaño del <b>módulo delantero</b> en las 2 sillas delanteras → aprieta el botón, mete los 2 pasadores, suelta: <b>clic</b>.",
 "Levanta la parte de atrás. Mete el travesaño del <b>módulo trasero</b> en las 2 sillas traseras → 2 pasadores: <b>clic</b>.",
 "Tira fuerte de cada módulo hacia afuera: no debe salir. Las ruedas originales quedan ~5 cm en el aire.",
 "Engancha la <b>correa de muñeca</b> al manillar.",
])}
<h3>⚡ C · Desenclachar</h3>
{pasos(["Botón de cada pasador → sácalo (queda colgando de su cordón) → saca el módulo. El coche vuelve a sus ruedas originales y se pliega normal."])}
</div>
{plano_crop(5, 160, 150, 132, 120)}
<h3>Revisión antes de cada salida</h3>
{check(["4 pasadores trabados (tira de cada uno)", "Soportes sin grietas, no se deslizan en la pata", "Tuercas de los ejes apretadas, ruedas sin juego",
        "El coche va derecho (si no, alinear)", "Correa de muñeca puesta"])}
<p class="peligro"><b>Ruedas EVA:</b> no se pinchan y son livianas, pero no amortiguan como un neumático con aire. Úsalas en pavimento, ciclovías y tierra compactada, a ritmo moderado.
El kit no tiene freno de mano: <b>siempre con correa de muñeca</b>. Patineta y hamaca <b>siempre desmontadas</b> al trotar.</p>
</section>

<section class="s2">
<h2>2 · Patineta hermano + sillín (rebatible)</h2>
{plano_crop(205, 25, 210, 135, 182)}
<h3>Materiales a comprar</h3>
{compras([
 ("Rueda de patín en línea 80 mm 82A", "2", "Falabella / Mercado Libre «ruedas patines 80mm»"),
 ("Rodamiento 608ZZ + espaciador 8 mm", "4 + 2", "suelen venir con las ruedas"),
 ("Pasador de bola con botón Ø8 mm, largo útil ≈ 65 mm, con cordón", "2", "enclachar los brazos a las patas"),
 ("Tubo redondo aluminio Ø20 mm", f"2 x ~{C['brazo'] + 20:.0f} mm", "brazos (cortar y ajustar)"),
 ("Tubo redondo aluminio Ø25 mm", "300 mm", "poste del sillín"),
 ("Perno M5x20 + tuerca", "12", "unir las 4 baldosas"),
 ("Perno M6x40 + tuerca", "4", "placa pivote"),
 ("Perno M6x35 + tuerca", "8", "placa central y horquillas de ruedas"),
 ("Perno M6x50 + tuerca", "8", "abrazaderas pivote (fijas en el coche)"),
 ("Perno M8x60 + tuerca autoblocante", "2", "ejes de las ruedas"),
 ("Perno M8x50 + tuerca autoblocante + 2 golillas nylon", "1", "bisagra del yugo"),
 ("Perno M10x60 + tuerca autoblocante + golillas", "1", "pivote giratorio"),
 ("Perno M5x35 + tuerca", "4", "fijar tubos en terminales y yugo"),
 ("Pasador con anilla tipo R Ø6 (o perno M6x45)", "1", "altura del sillín"),
 ("Lija antideslizante autoadhesiva (grip tape) 40x30 cm", "1", "superficie de la tabla"),
 ("Cinta 25 mm (1 m) + hebilla de seguridad 25 mm (click)", "1", "correa de plegado"),
])}
<h3>Piezas impresas</h3>
{piezas_tabla("02_patineta")}

<h3>A · Preparación (una sola vez)</h3>
{pasos([
 "Une las 4 baldosas con 12 x M5x20. Atornilla arriba: <code>placa_pivote</code> adelante-centro (4 x M6x40), <code>placa_central_asiento</code> al centro (4 x M6x35). Abajo-atrás: 2 <code>horquilla_ruedita</code> (4 x M6x35).",
 "Ruedas: 2 rodamientos + espaciador, eje M8x60, autoblocante. Pega la lija.",
 "Pivote: M10x60 desde arriba por <code>bloque_giratorio</code> + placa + tabla; autoblocante abajo, que gire suave.",
 f"Corta los tubos Ø20 (~{C['brazo']:.0f} mm). Un extremo al <code>yugo_brazos</code>, otro a un <code>terminal_brazo</code>; perfora Ø5 por la pieza y fija con M5x35.",
 "Lengüeta del yugo entre las orejas del bloque giratorio con M8x50 + golillas de nylon (queda fija; es una bisagra).",
 "Instala las 2 <code>abrazadera_pivote_pata</code> (A + tapa, 4 x M6x50) en las patas traseras, <b>justo encima</b> del soporte con silla trasero, oreja hacia atrás. Quedan fijas.",
 "Sillín: poste Ø25 perforado cada 25 mm; altura con el pasador R. Los pies de la niña deben apoyar en la tabla.",
])}
<div class="rapido"><h3>⚡ B · Poner la patineta (≈ 20 s)</h3>
{pasos(["Acerca la patineta por detrás. Pon cada <code>terminal_brazo</code> en la <b>cara interior</b> de la oreja de su abrazadera.",
        "Botón → mete el pasador Ø8 por oreja + terminal → <b>clic</b>. Repite al otro lado. Tira para comprobar."])}
<h3>⚡ C · Rebatir (plegar) cuando la niña quiere caminar (≈ 5 s)</h3>
{pasos(["Toma la patineta por el yugo y levántala: los brazos giran en las orejas y la tabla queda <b>colgando vertical detrás del coche</b>.",
        "Pasa la correa por la tabla y <b>abrocha la hebilla</b> (click) al anclaje superior de la hamaca (o al tubo del manillar).",
        "Para usarla de nuevo: suelta la hebilla y bájala. Para sacarla del todo: los 2 pasadores."])}
</div>
{check(["Pasadores trabados", "Pivote gira suave y sin juego", "Ruedas giran libres", "Sillín a la altura correcta y con pasador puesto"])}
<p class="peligro">Solo caminando. La niña va afirmada al manillar o con el cinturón de la hamaca.</p>
</section>

<section class="s3">
<h2>3 · Hamaca (modo siesta)</h2>
<h3>Materiales a comprar</h3>
{compras([
 ("Lona Cordura 600D", "40 x 120 cm", "tienda de telas / Mercado Libre"),
 ("Espuma 10 mm", "35 x 55 cm", "respaldo acolchado"),
 ("Cinta de polipropileno 25 mm", "6 m", ""),
 ("Hebilla de seguridad 25 mm (side release, click)", "5", "4 para enclachar las cintas + 1 cinturón"),
 ("Hebilla escalera 25 mm (regulador)", "4", "ajustar largo de cada cinta"),
 ("Perno M5x35 + tuerca", "4", "anclajes del manillar"),
 ("Hilo de poliéster grueso", "1", ""),
])}
<h3>Piezas impresas</h3>
{piezas_tabla("03_hamaca")}
<p>Los anclajes inferiores ya están en las <code>abrazadera_pivote_pata</code> (ranura para cinta). El fondo de la hamaca se amarra a los 4 ojales del <code>asiento_sillin</code>.</p>
<h3>Costura</h3>
<pre style="font-size:8.5pt;line-height:1.25">
        ┌──────── 38 cm ────────┐
        │  bolsillo espuma 10mm │  ← respaldo + cabecera (alas de 8 cm
        │      (35 x 55 cm)     │     a cada lado, a la altura de la cabeza)
   70cm │                       │
        ├───────────────────────┤  ← cinturón con hebilla de seguridad
        │   asiento (38 x 30)   │     4 cintas cortas → ojales del sillín
        ├───────────────────────┤
   20cm │    faldón delantero   │  ← 2 cintas → anclajes inferiores
        └───────────────────────┘
</pre>
{pasos(["Cose 2 cintas arriba y 2 abajo con costura en «caja con X». Cada cinta termina en <b>macho de hebilla de seguridad</b>.",
        "En cada anclaje (manillar y abrazadera pivote) deja fija una cinta corta con la <b>hembra</b> y una hebilla escalera para regular.",
        "Agrega cinta de entrepierna (faldón → cinturón) para que no se deslice."])}
<div class="rapido"><h3>⚡ Poner / sacar (≈ 30 s)</h3>
{pasos(["Patineta puesta y sillín instalado.", "Abrocha las 4 hebillas: <b>clic, clic, clic, clic</b>. Amarra el fondo a los ojales del sillín.",
        "Regula las cintas superiores: respaldo reclinado ~30°.",
        "Sienta a la niña en el sillín <b>mirando hacia ti</b>, espalda y cabeza en la lona. Abrocha el cinturón."])}</div>
<p class="peligro">Solo caminando. El peso de la niña debe ir sobre el sillín, no colgado del manillar. Nunca sueltes el coche con la niña en la hamaca.
Que el mentón no quede pegado al pecho; revísala seguido.</p>
</section>

<section class="s4">
<h2>4 · Bandeja con portavasos</h2>
<h3>Materiales a comprar</h3>
{compras([
 ("Perno M5x25 + tuerca", "4", "abrazaderas al manillar"),
 ("Perno M5x20", "4", "bandeja a las abrazaderas (tuercas cautivas)"),
 ("Perno M4x20 + tuerca", "3", "unir las 2 mitades"),
 ("Perno M4x12", "4", "portavasos (tuercas cautivas)"),
 ("Tira de cámara de bicicleta", "2", "agarre en el manillar"),
])}
<h3>Piezas impresas</h3>
{piezas_tabla("04_bandeja")}
{pasos(["Une las 2 mitades con 3 x M4x20 por los nervios centrales.",
        "Abrazaderas del manillar (superior + inferior, 2 x M5x25) a <b>180 mm</b> entre centros, pestaña hacia adelante y horizontal.",
        "Atornilla la bandeja a las pestañas (4 x M5x20) y un portavasos bajo cada borde lateral (2 x M4x12 c/u).",
        "Calzos de TPU para vasos de 72 o 62 mm. Los vasos impresos sirven para snacks secos; para líquidos usa vasos comerciales.",
        "La bandeja puede quedar siempre puesta: no impide plegar el coche si la capota se abre hacia atrás (verifícalo)."])}
</section>

<section class="s0">
<h2>Seguridad</h2>
{check(["Prueba de carga antes de subir a los niños: 20 kg (saco de arena) en el asiento y 20 kg en la patineta. Camina 2 km y revisa.",
        "Trote: correa de muñeca siempre; sin freno de mano → ritmo moderado, nada de bajadas fuertes. Bebé con arnés de 5 puntas y respaldo algo reclinado.",
        "Patineta, sillín y hamaca: solo caminando.",
        "Imprime en PETG/ASA, nunca PLA (se deforma al sol o dentro del auto).",
        "Antes de cada salida: pasadores trabados, piezas sin grietas, pernos apretados.",
        "Esta es una modificación casera: Maxi-Cosi no la aprueba y anula la garantía."])}
<h3>Lista total de cortes de metal</h3>
<ul>
<li>Tubo 20x20x2: {C['trav_del']:.0f} mm + {C['trav_tras']:.0f} mm</li>
<li>Pletina 30x5: 2 x {fd['largo']:.0f} mm (delantera) + 4 x {ft['largo']:.0f} mm (traseras)</li>
<li>Tubo Ø20: 2 x ~{C['brazo']:.0f} mm · Tubo Ø25: 1 x 300 mm</li>
</ul>
<p>Trocha trasera modo trote: {C['trocha']:.0f} mm · ancho total ≈ {C['ancho_total']:.0f} mm (saca el módulo trasero para pasar puertas angostas).</p>
</section>

<div class="anexo">{PLANO.replace('width="420mm" height="297mm"', 'width="420mm" height="297mm" preserveAspectRatio="xMidYMid meet"')}</div>
</body></html>"""

out_html = os.path.join(DOCS, "manual_armado.html")
open(out_html, "w").write(html)
js = f"""
const {{chromium}} = require('playwright');
(async () => {{
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://{out_html}', {{waitUntil: 'load'}});
  await p.pdf({{path: '{os.path.join(DOCS, "manual_armado.pdf")}', preferCSSPageSize: true, printBackground: true}});
  await b.close();
}})();"""
subprocess.run(["node", "-e", js], check=True)
print("ok docs/manual_armado.pdf")
