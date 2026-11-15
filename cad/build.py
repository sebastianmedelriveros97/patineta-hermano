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

    ("01_kit_running", "soporte_brazo_trasero_A", 2, "PETG/ASA 100%", lambda: X.rear_axle_bracket()[0]),
    ("01_kit_running", "soporte_brazo_trasero_B_tapa", 2, "PETG/ASA 60%", lambda: X.rear_axle_bracket()[1]),
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


def _plantilla(nombre, titulo, holes, largo, nota):
    w = P.PLETINA_ANCHO
    circ = "".join(f'<circle cx="{x:.1f}" cy="{w/2}" r="{d/2:.2f}" fill="none" stroke="red" stroke-width="0.3"/>'
                   f'<line x1="{x-3:.1f}" y1="{w/2}" x2="{x+3:.1f}" y2="{w/2}" stroke="red" stroke-width="0.15"/>'
                   f'<text x="{x:.1f}" y="{w+6}" font-size="3.5" text-anchor="middle" font-family="sans-serif">{x:.0f}</text>'
                   for x, d in holes)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{largo+20:.0f}mm" height="{w+60}mm" viewBox="-10 -40 {largo+20:.0f} {w+60}">
<rect x="-10" y="-40" width="{largo+20:.0f}" height="{w+60}" fill="white"/>
<rect x="0" y="0" width="{largo:.1f}" height="{w}" fill="none" stroke="black" stroke-width="0.3"/>
<line x1="0" y1="{w/2}" x2="{largo:.1f}" y2="{w/2}" stroke="gray" stroke-width="0.15" stroke-dasharray="2,2"/>
{circ}
<text x="0" y="-28" font-size="5" font-family="sans-serif">{titulo} — ESCALA 1:1 (imprimir al 100 %, comprobar la regla de 100 mm)</text>
<text x="0" y="-20" font-size="3.6" font-family="sans-serif">{nota}</text>
<line x1="0" y1="-12" x2="100" y2="-12" stroke="black" stroke-width="0.5"/><text x="102" y="-11" font-size="4" font-family="sans-serif">100 mm</text>
</svg>'''
    open(os.path.join(ROOT, "docs", nombre), "w").write(svg)


def extras():
    """Plantillas 1:1 de pletinas y medidas de corte de metales."""
    import math
    import geom
    lf, ang = X.front_geometry()
    s1, s2 = 30, 66
    start = 12
    Lf = lf - start + 22
    _plantilla("plantilla_pletina_horquilla_1a1.svg", f"Pletina HORQUILLA delantera {P.PLETINA_ANCHO:.0f}x{P.PLETINA_ESPESOR:.0f} (hacer 2)",
               [(s1 - start, 6.5), (s2 - start, 6.5), (lf - start, P.EJE_DELANTERO + 0.5)], Lf,
               f"Largo {Lf:.0f} mm. Agujeros M6 y eje Ø{P.EJE_DELANTERO+0.5:.1f}. En UNA pletina el eje como ranura de 16 mm para alinear.")
    p1, p2, ax, d, hx, hy = X.rear_arm_geometry()
    la = math.hypot(ax[0] - p1[0], ax[1] - p1[1])
    l12 = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    Lr = la + 15 + 20
    _plantilla("plantilla_pletina_brazo_trasero_1a1.svg", f"Pletina BRAZO trasero {P.PLETINA_ANCHO:.0f}x{P.PLETINA_ESPESOR:.0f} (hacer 2)",
               [(15, 8.5), (15 + l12, 8.5), (15 + la, P.RUEDA_RUNNING_BUJE + 0.5)], Lr,
               f"Largo {Lr:.0f} mm. 2 agujeros M8 (Ø8,5) y eje Ø{P.RUEDA_RUNNING_BUJE+0.5:.1f}. Va por el lado INTERIOR de la pata.")
    track = P.ANCHO_CHASIS - 2 * hy + 2 * (P.SEPARADOR_TRASERO + 50 + 25)
    eje = track
    travesano = P.ANCHO_CHASIS + 60
    lat, n, tilt, theta = X._arm_geometry()
    brazo = n - 16 - 6 - 8 - 8 - 25
    txt = (f"- Eje trasero (acero liso Ø{P.RUEDA_RUNNING_BUJE:.0f}, SAE 1020/1045): **{eje:.0f} mm**; perforar Ø4 en cada punta para pasador R\n"
           f"- Travesaño delantero (tubo 20x20): **{travesano:.0f} mm**\n"
           f"- Pletinas horquilla 30x5: **2 x {Lf:.0f} mm** (ver `plantilla_pletina_horquilla_1a1.svg`)\n"
           f"- Pletinas brazo trasero 30x5: **2 x {Lr:.0f} mm** (ver `plantilla_pletina_brazo_trasero_1a1.svg`)\n"
           f"- Brazos patineta (tubo Ø20): **2 x ~{brazo:.0f} mm** (cortar 20 mm más largo y ajustar)\n"
           f"- Poste asiento (tubo Ø25): **1 x 300 mm**, perforar Ø6,5 cada 25 mm para regular altura\n")
    open(os.path.join(ROOT, "docs", "cortes_metal.md"), "w").write("# Cortes de metal (generado por cad/build.py)\n\n" + txt)
    print(txt)


if __name__ == "__main__" and len(sys.argv) == 1:
    extras()
