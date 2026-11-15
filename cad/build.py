"""Genera todos los STL en ../stl y una tabla de piezas.
Uso:  python3 cad/build.py"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import params as P
import parts as X
from lib import export

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "stl")

lf, ang = X.front_geometry()
sep = P.SEPARADOR_TRASERO

# (carpeta, archivo, cantidad, material, función)
PIEZAS = [
    ("00_pruebas", "prueba_perfil_pata_trasera", 1, "PLA", lambda: X.test_ring(P.PATA_TRASERA_ANCHO, P.PATA_TRASERA_FONDO, P.PATA_TRASERA_RADIO)),
    ("00_pruebas", "prueba_perfil_pata_delantera", 1, "PLA", lambda: X.test_ring(P.PATA_DELANTERA_ANCHO, P.PATA_DELANTERA_FONDO, P.PATA_DELANTERA_RADIO)),
    ("00_pruebas", "prueba_manillar", 1, "PLA", lambda: X.test_round(P.MANILLAR_DIAM)),
    ("00_pruebas", "prueba_tubo_lateral_manillar", 1, "PLA", lambda: X.test_round(P.TUBO_LATERAL_MANILLAR_DIAM)),

    ("01_kit_running", "soporte_eje_trasero_A", 2, "PETG/ASA 100%", lambda: X.rear_axle_bracket()[0]),
    ("01_kit_running", "soporte_eje_trasero_B_tapa", 2, "PETG/ASA 60%", lambda: X.rear_axle_bracket()[1]),
    ("01_kit_running", f"separador_eje_{int(sep)}mm", 2, "PETG 60%", lambda: X.axle_spacer(sep)),
    ("01_kit_running", "collarin_eje", 4, "PETG 100%", X.axle_collar),
    ("01_kit_running", "soporte_travesano_delantero_A", 2, "PETG/ASA 100%", lambda: X.front_leg_bracket()[0]),
    ("01_kit_running", "soporte_travesano_delantero_B_tapa", 2, "PETG/ASA 60%", lambda: X.front_leg_bracket()[1]),
    ("01_kit_running", "separador_horquilla", 1, "PETG/ASA 100%", X.fork_spacer),
    ("01_kit_running", "tapon_tubo_cuadrado", 2, "TPU/PETG", X.bar_end_cap),

    ("02_patineta", "baldosa_tabla_del_izq", 1, "PETG 40% giroide", lambda: X.deck_tile(0, 1)),
    ("02_patineta", "baldosa_tabla_del_der", 1, "PETG 40% giroide", lambda: X.deck_tile(1, 1)),
    ("02_patineta", "baldosa_tabla_tras_izq", 1, "PETG 40% giroide", lambda: X.deck_tile(0, 0)),
    ("02_patineta", "baldosa_tabla_tras_der", 1, "PETG 40% giroide", lambda: X.deck_tile(1, 0)),
    ("02_patineta", "horquilla_ruedita", 2, "PETG 100%", X.wheel_fork),
    ("02_patineta", "placa_pivote", 1, "PETG 100%", X.kingpin_plate),
    ("02_patineta", "bloque_giratorio", 1, "PETG 100%", X.swivel_block),
    ("02_patineta", "yugo_brazos", 1, "PETG 100%", X.yoke),
    ("02_patineta", "terminal_brazo", 2, "PETG 100%", X.arm_end),
    ("02_patineta", "abrazadera_pivote_pata_A", 2, "PETG/ASA 100%", lambda: X.board_leg_pivot()[0]),
    ("02_patineta", "abrazadera_pivote_pata_B_tapa", 2, "PETG/ASA 60%", lambda: X.board_leg_pivot()[1]),
    ("02_patineta", "placa_central_asiento", 1, "PETG 100%", X.seat_plate),
    ("02_patineta", "asiento_sillin", 1, "PETG 30%", X.saddle),

    ("03_hamaca", "anclaje_manillar_A", 2, "PETG 100%", lambda: X.handle_anchor()[0]),
    ("03_hamaca", "anclaje_manillar_B_tapa", 2, "PETG 60%", lambda: X.handle_anchor()[1]),

    ("04_bandeja", "bandeja_mitad_izq", 1, "PETG 25%", lambda: X.tray_half(-1)),
    ("04_bandeja", "bandeja_mitad_der", 1, "PETG 25%", lambda: X.tray_half(1)),
    ("04_bandeja", "abrazadera_manillar_superior", 2, "PETG 60%", lambda: X.tray_bar_clamp()[0]),
    ("04_bandeja", "abrazadera_manillar_inferior", 2, "PETG 60%", lambda: X.tray_bar_clamp()[1]),
    ("04_bandeja", "portavasos", 2, "PETG 25%", X.cup_holder),
    ("04_bandeja", "calzo_vaso_72mm", 2, "TPU 95A", lambda: X.cup_shim(72)),
    ("04_bandeja", "calzo_vaso_62mm", 2, "TPU 95A", lambda: X.cup_shim(62)),
    ("04_bandeja", "vaso_350ml", 2, "PETG / PP", X.cup),
]


def main(only=None):
    rows = []
    for carpeta, nombre, cant, mat, fn in PIEZAS:
        if only and only not in nombre:
            continue
        t = time.time()
        m = fn()
        path = os.path.join(OUT, carpeta, nombre + ".stl")
        ext, vol = export(m, path)
        ok = "OK" if max(ext[0], ext[1]) <= P.CAMA else "¡NO CABE!"
        g = vol / 1000 * 1.27  # PETG aprox. si fuera sólido
        rows.append((carpeta, nombre, cant, mat, ext, ok))
        print(f"{carpeta}/{nombre:38s} x{cant}  {ext[0]:6.1f} x {ext[1]:6.1f} x {ext[2]:6.1f} mm  {ok}  ({time.time()-t:.1f}s)")
    if only:
        return
    with open(os.path.join(ROOT, "docs", "lista_piezas_impresas.md"), "w") as f:
        f.write("# Lista de piezas impresas (generada por cad/build.py)\n\n")
        f.write(f"Cama configurada: {P.CAMA} mm. Las medidas son X x Y x Z en la orientación de impresión.\n\n")
        f.write("| Carpeta | Archivo STL | Cant. | Material / relleno | Medidas (mm) | Cabe |\n|---|---|---|---|---|---|\n")
        for c, n, q, m, e, ok in rows:
            f.write(f"| {c} | `{n}.stl` | {q} | {m} | {e[0]:.0f} x {e[1]:.0f} x {e[2]:.0f} | {ok} |\n")
        f.write(f"\n**Geometría horquilla delantera calculada:** distancia centro travesaño → eje delantero = "
                f"**{lf:.0f} mm**, inclinación {ang:.1f}° (negativo = hacia abajo).\n")


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    main(sys.argv[1] if len(sys.argv) > 1 else None)


def extras():
    """Plantilla 1:1 de la pletina y medidas de corte de metales."""
    import math
    lf, ang = X.front_geometry()
    s1, s2 = 30, 66
    start = 12
    L = lf - start + 22
    w = P.PLETINA_ANCHO
    h1, h2, ax = s1 - start, s2 - start, lf - start
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{L+20}mm" height="{w+60}mm" viewBox="-10 -40 {L+20} {w+60}">
<rect x="0" y="0" width="{L:.1f}" height="{w}" fill="none" stroke="black" stroke-width="0.3"/>
<line x1="0" y1="{w/2}" x2="{L:.1f}" y2="{w/2}" stroke="gray" stroke-width="0.15" stroke-dasharray="2,2"/>
<circle cx="{h1}" cy="{w/2}" r="3.25" fill="none" stroke="red" stroke-width="0.3"/>
<circle cx="{h2}" cy="{w/2}" r="3.25" fill="none" stroke="red" stroke-width="0.3"/>
<circle cx="{ax:.1f}" cy="{w/2}" r="{P.EJE_DELANTERO/2+0.25}" fill="none" stroke="red" stroke-width="0.3"/>
<text x="0" y="-28" font-size="5" font-family="sans-serif">Pletina horquilla {w:.0f}x{P.PLETINA_ESPESOR:.0f} mm  -  ESCALA 1:1 (imprimir al 100%, verificar regla de 100 mm)</text>
<text x="0" y="-20" font-size="4" font-family="sans-serif">Largo {L:.0f} mm. Agujeros M6 a {h1:.0f} y {h2:.0f} mm; eje Ø{P.EJE_DELANTERO+0.5:.1f} a {ax:.0f} mm del extremo. Hacer 2 (en una, el eje como ranura de 16 mm para alinear).</text>
<line x1="0" y1="-12" x2="100" y2="-12" stroke="black" stroke-width="0.5"/>
<text x="102" y="-11" font-size="4" font-family="sans-serif">100 mm</text>
</svg>'''
    open(os.path.join(ROOT, "docs", "plantilla_pletina_horquilla_1a1.svg"), "w").write(svg)
    eje = P.ANCHO_CHASIS + 2 * (P.SEPARADOR_TRASERO + 50 + 25)
    travesano = P.ANCHO_CHASIS + 60
    lat, n, tilt, theta = X._arm_geometry()
    brazo = n - 16 - 6 - 8 - 8 - 25
    txt = (f"- Eje trasero (barra roscada M12): **{eje:.0f} mm** (ajusta tras presentar ruedas)\n"
           f"- Travesaño delantero (tubo 20x20): **{travesano:.0f} mm**\n"
           f"- Pletinas horquilla 30x5: **2 x {L:.0f} mm** — agujeros a {h1:.0f} / {h2:.0f} / {ax:.0f} mm "
           f"(ver `plantilla_pletina_horquilla_1a1.svg`)\n"
           f"- Brazos patineta (tubo Ø20): **2 x ~{brazo:.0f} mm** (cortar 20 mm más largo y ajustar)\n"
           f"- Poste asiento (tubo Ø25): **1 x 300 mm**, perforar Ø6.5 cada 25 mm para regular altura\n")
    open(os.path.join(ROOT, "docs", "cortes_metal.md"), "w").write("# Cortes de metal (generado por cad/build.py)\n\n" + txt)
    print(txt)


if __name__ == "__main__" and len(sys.argv) == 1:
    extras()
