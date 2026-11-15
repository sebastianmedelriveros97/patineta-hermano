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


# (carpeta, archivo, cantidad, material, función)
PIEZAS = [
    ("00_pruebas", "prueba_perfil_pata_trasera", 1, "PLA", lambda: X.test_ring(P.PATA_TRASERA_ANCHO, P.PATA_TRASERA_FONDO, P.PATA_TRASERA_RADIO)),
    ("00_pruebas", "prueba_perfil_pata_delantera", 1, "PLA", lambda: X.test_ring(P.PATA_DELANTERA_ANCHO, P.PATA_DELANTERA_FONDO, P.PATA_DELANTERA_RADIO)),
    ("00_pruebas", "prueba_manillar", 1, "PLA", lambda: X.test_round(P.MANILLAR_DIAM)),
    ("00_pruebas", "prueba_tubo_lateral_manillar", 1, "PLA", lambda: X.test_round(P.TUBO_LATERAL_MANILLAR_DIAM)),

    ("01_kit_running", "soporte_silla_trasero_A", 2, "PETG/ASA 100%", lambda: X.saddle_bracket(True)[0]),
    ("01_kit_running", "soporte_silla_trasero_B_tapa", 2, "PETG/ASA 60%", lambda: X.saddle_bracket(True)[1]),
    ("01_kit_running", "soporte_silla_delantero_A", 2, "PETG/ASA 100%", lambda: X.saddle_bracket(False)[0]),
    ("01_kit_running", "soporte_silla_delantero_B_tapa", 2, "PETG/ASA 60%", lambda: X.saddle_bracket(False)[1]),
    ("01_kit_running", "bloque_horquilla_trasera", 2, "PETG/ASA 100%", lambda: X.fork_block(True)),
    ("01_kit_running", "bloque_horquilla_delantera", 1, "PETG/ASA 100%", lambda: X.fork_block(False)),
    ("01_kit_running", "tapon_tubo_cuadrado", 4, "TPU/PETG", X.bar_end_cap),

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


def cortes():
    """Medidas de metal derivadas de la geometría (se usan en docs y manual)."""
    import geom
    s1, s2 = X.FORK_S1, X.FORK_S2
    start = 12
    out = {}
    for key, tube, axle in (("delantera", geom.TRAVESANO, geom.FRONT_AXLE), ("trasera", geom.REAR_BEAM, geom.REAR_AXLE)):
        lf, ang, dx, dz = geom.fork(tube, axle)
        out[key] = dict(largo=lf - start + 22, h1=s1 - start, h2=s2 - start, eje=lf - start, ang=ang)
    out["trav_del"] = P.ANCHO_CHASIS + 60
    out["trav_tras"] = 2 * (geom.REAR_WHEEL_Y + P.BUJE_ANCHO / 2 + P.PLETINA_ESPESOR + 8)
    lat, n, tilt, theta = X._arm_geometry()
    out["brazo"] = n - 16 - 6 - 8 - 8 - 25
    out["trocha"] = 2 * geom.REAR_WHEEL_Y
    out["ancho_total"] = 2 * (geom.REAR_WHEEL_Y + P.BUJE_ANCHO / 2 + P.PLETINA_ESPESOR + 8)
    return out


def extras():
    """Plantillas 1:1 de pletinas y medidas de corte de metales."""
    import geom
    c = cortes()
    for key, cant in (("delantera", 2), ("trasera", 4)):
        f = c[key]
        _plantilla(f"plantilla_pletina_horquilla_{key}_1a1.svg",
                   f"Pletina HORQUILLA {key.upper()} {P.PLETINA_ANCHO:.0f}x{P.PLETINA_ESPESOR:.0f} (hacer {cant})",
                   [(f["h1"], 6.5), (f["h2"], 6.5), (f["eje"], P.EJE_RUEDA + 0.5)]
                   + ([(f["eje"] - 80, 6.5)] if key == "trasera" else []), f["largo"],
                   f"Largo {f['largo']:.0f} mm. 2 agujeros M6 (Ø6,5) y eje Ø{P.EJE_RUEDA + 0.5:.1f}. "
                   f"En UNA pletina de cada horquilla el eje como ranura de 16 mm (alineación)."
                   + (" Agujero a eje-80: FRENO de estacionamiento (pasador entre los rayos), solo en las 2 pletinas exteriores." if key == "trasera" else ""))
    for old in ("plantilla_pletina_horquilla_1a1.svg", "plantilla_pletina_brazo_trasero_1a1.svg"):
        p = os.path.join(ROOT, "docs", old)
        if os.path.exists(p):
            os.remove(p)
    fd, ft = c["delantera"], c["trasera"]
    txt = (f"- Travesaño delantero (tubo 20x20x2): **{c['trav_del']:.0f} mm** — perforar Ø6,5 vertical donde caen los 2 pasadores y el bloque\n"
           f"- Travesaño trasero (tubo 20x20x2): **{c['trav_tras']:.0f} mm** — ídem (2 pasadores + 2 bloques)\n"
           f"- Pletinas horquilla delantera 30x5: **2 x {fd['largo']:.0f} mm** (`plantilla_pletina_horquilla_delantera_1a1.svg`)\n"
           f"- Pletinas horquillas traseras 30x5: **4 x {ft['largo']:.0f} mm** (`plantilla_pletina_horquilla_trasera_1a1.svg`)\n"
           f"- Brazos patineta (tubo Ø20): **2 x ~{c['brazo']:.0f} mm** (cortar 20 mm más largo y ajustar)\n"
           f"- Poste asiento (tubo Ø25): **1 x 300 mm**, perforar Ø6,5 cada 25 mm para regular altura\n"
           f"\nTrocha trasera {c['trocha']:.0f} mm · ancho total modo trote ≈ {c['ancho_total']:.0f} mm\n")
    open(os.path.join(ROOT, "docs", "cortes_metal.md"), "w").write("# Cortes de metal (generado por cad/build.py)\n\n" + txt)
    print(txt)
    for m in geom.checks():
        print(m)


if __name__ == "__main__" and len(sys.argv) == 1:
    extras()
