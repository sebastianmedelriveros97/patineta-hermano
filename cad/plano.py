"""Genera docs/plano_general.svg — plano A3 a escala 1:10 con el coche y todos
los accesorios, usando la MISMA geometría que las piezas (params.py / geom.py).
Uso:  python3 cad/plano.py"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import geom as G
import params as P
import parts as X

ESC = 0.1  # 1:10  (mm reales -> mm de papel)
out = []

C_FRAME = "#455a64"
C_SOFT = "#b0bec5"
C_FAB = "#cfd8dc"
C_RUN = "#e65100"
C_STEEL = "#546e7a"
C_BOARD = "#1565c0"
C_HAM = "#2e7d32"
C_TRAY = "#6a1b9a"
C_KID = "#f3d9c4"


def add(s):
    out.append(s)


class View:
    """Vista: mapea (x real, z real) -> papel. x real hacia atrás = derecha."""

    def __init__(self, ox, oy):
        self.ox, self.oy = ox, oy

    def p(self, x, z):
        return (self.ox + x * ESC, self.oy - z * ESC)

    def line(self, a, b, color=C_FRAME, w=0.3, dash=None, cap="round"):
        (x1, y1), (x2, y2) = self.p(*a), self.p(*b)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{w}" stroke-linecap="{cap}"{d}/>')

    def tube(self, a, b, diam=22, color=C_FRAME):
        self.line(a, b, color, diam * ESC)

    def circle(self, c, r, stroke=C_FRAME, fill="none", w=0.3, dash=None):
        x, y = self.p(*c)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r*ESC:.2f}" stroke="{stroke}" fill="{fill}" stroke-width="{w}"{d}/>')

    def poly(self, pts, stroke=C_FRAME, fill="none", w=0.3, dash=None, close=True):
        s = " ".join(f"{self.p(*q)[0]:.2f},{self.p(*q)[1]:.2f}" for q in pts)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        tag = "polygon" if close else "polyline"
        add(f'<{tag} points="{s}" stroke="{stroke}" fill="{fill}" stroke-width="{w}" stroke-linejoin="round"{d}/>')

    def rect(self, x0, z0, x1, z1, **k):
        self.poly([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], **k)

    def path(self, d_real, stroke, fill="none", w=0.3, dash=None):
        # d_real: lista de (cmd, [x,z,...])
        s = ""
        for cmd, nums in d_real:
            s += cmd
            for i in range(0, len(nums), 2):
                x, y = self.p(nums[i], nums[i + 1])
                s += f" {x:.2f},{y:.2f}"
            s += " "
        d = f' stroke-dasharray="{dash}"' if dash else ""
        add(f'<path d="{s}" stroke="{stroke}" fill="{fill}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{d}/>')

    def text(self, pos, s, color="#222", size=2.4, anchor="start", weight="normal"):
        x, y = self.p(*pos)
        add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>')

    def callout(self, at, txt_pos, s, color, anchor="start"):
        self.line(at, txt_pos, color, 0.18)
        self.circle(at, 6, stroke=color, fill=color, w=0.1)
        tx, tz = txt_pos
        self.text((tx + (8 if anchor == "start" else -8), tz - 8), s, color, 2.3, anchor)

    def dim(self, a, b, off, label, vertical=False):
        """cota entre a y b (reales), desplazada 'off' (real) perpendicular"""
        if vertical:
            x = a[0] + off
            p1, p2 = (x, a[1]), (x, b[1])
            self.line(a, (x + (8 if off > 0 else -8), a[1]), "#777", 0.12)
            self.line(b, (x + (8 if off > 0 else -8), b[1]), "#777", 0.12)
        else:
            z = a[1] + off
            p1, p2 = (a[0], z), (b[0], z)
            self.line(a, (a[0], z + (8 if off > 0 else -8)), "#777", 0.12)
            self.line(b, (b[0], z + (8 if off > 0 else -8)), "#777", 0.12)
        (x1, y1), (x2, y2) = self.p(*p1), self.p(*p2)
        add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#333" stroke-width="0.15" marker-start="url(#ar)" marker-end="url(#ar)"/>')
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if vertical:
            add(f'<text x="{mx - 0.8:.2f}" y="{my:.2f}" font-size="2.3" fill="#333" text-anchor="middle" transform="rotate(-90 {mx - 0.8:.2f} {my:.2f})">{label}</text>')
        else:
            add(f'<text x="{mx:.2f}" y="{my - 0.8:.2f}" font-size="2.3" fill="#333" text-anchor="middle">{label}</text>')


# ---------------------------------------------------------------------------
def shift(pt, dz):
    return (pt[0], pt[1] + dz)


def wheel(v, c, r, tire=None, color=C_FRAME, dash=None, spokes=0):
    tire = tire or r * 0.22
    v.circle(c, r, stroke=color, fill="#263238" if not dash else "none", w=0.3 if not dash else 0.25, dash=dash)
    v.circle(c, r - tire, stroke=color, fill="#eceff1" if not dash else "none", w=0.25, dash=dash)
    v.circle(c, r * 0.12, stroke=color, fill=color if not dash else "none", w=0.2, dash=dash)
    for k in range(spokes):
        a = math.pi * 2 * k / spokes
        v.line(c, (c[0] + math.cos(a) * (r - tire), c[1] + math.sin(a) * (r - tire)), "#90a4ae", 0.12)


def handle_points():
    """tubo recto (prolongación de la pata delantera) + asa de cuero en curva hasta el manillar"""
    up = G.FRONT_UP
    zt = 960.0
    t = (zt - G.FRONT_LEG_BOT[1]) / up[1]
    top = (G.FRONT_LEG_BOT[0] + up[0] * t, zt)
    return top


def stroller_side(v, dz, orig_dash=False):
    """Maxi-Cosi Leona 2 en vista lateral, calibrado con fotos (chasis en X)."""
    H = shift(G.HINGE, dz)
    FL = shift(G.FRONT_LEG_BOT, dz)
    RL = shift(G.REAR_LEG_BOT, dz)
    HB = (P.MANILLAR_X, P.MANILLAR_Z + dz)
    TOP = shift(handle_points(), dz)
    S = lambda pts: [shift(q, dz) for q in pts]
    dash = "1,0.8" if orig_dash else None
    # cesto
    v.poly(S([(55, 150), (370, 150), (425, 270), (405, 395), (110, 400), (40, 260)]), stroke=C_SOFT, fill="url(#mesh)", w=0.25)
    # ruedas originales
    wheel(v, shift(G.FRONT_HUB, dz), G.RF0, color=C_FRAME, dash=dash)
    wheel(v, shift(G.REAR_HUB, dz), G.RR0, color=C_FRAME, dash=dash)
    # giratorio delantero (horquilla de un lado)
    v.poly(S([(5, 195), (40, 195), (22, 95), (-12, 100)]), stroke=C_FRAME, fill="#37474f", w=0.2)
    # conjunto trasero: soporte + resorte + eje con freno central
    v.poly(S([(392, 205), (418, 188), (478, 128), (470, 100), (448, 100), (395, 168)]), stroke=C_FRAME, fill="#37474f", w=0.2)
    zz = [(436, 158), (452, 150), (436, 142), (452, 134), (436, 126), (452, 118)]
    v.poly(S(zz), stroke="#b0bec5", fill="none", w=0.25, close=False)
    # chasis en X
    v.tube(FL, TOP, 24)
    v.tube(RL, H, 24)
    knob = shift(((G.FRONT_LEG_BOT[0] + G.FRONT_UP[0] * (776 - G.FRONT_LEG_BOT[1]) / G.FRONT_UP[1]), 776), dz)
    # asa de cuero
    v.path([("M", [TOP[0], TOP[1]]), ("C", [TOP[0] + 60, TOP[1] + 90, HB[0] - 60, HB[1] + 40, HB[0], HB[1]])], stroke="#8d5524", w=3.0)
    v.circle(HB, 15, stroke="#5d4037", fill="#8d5524", w=0.2)
    v.circle(knob, 34, stroke="#263238", fill="#455a64", w=0.25)
    # asiento: cojín + apoyapiernas + respaldo
    v.poly(S([(265, 455), (150, 470), (-95, 430), (-100, 470), (150, 515), (280, 505)]), stroke="#2e5d4f", fill="#4f7f6f", w=0.25)
    v.poly(S([(265, 470), (470, 950), (420, 975), (215, 500)]), stroke="#2e5d4f", fill="#4f7f6f", w=0.25)
    # capota plegada sobre el respaldo
    v.path([("M", [330, 780 + dz]), ("C", [380, 1000 + dz, 520, 1040 + dz, 560, 960 + dz]), ("L", [505, 860 + dz]), ("Z", [])], stroke="#2e5d4f", fill="#3f6b5d", w=0.25)
    # barra frontal (bumper) de cuero
    v.tube(shift((150, 590), dz), shift((-30, 640), dz), 22, "#8d5524")
    v.circle(H, 45, stroke="#263238", fill="#37474f", w=0.25)
    # bebé (1 año)
    v.circle(shift((335, 790), dz), 62, stroke="#c8a58c", fill=C_KID, w=0.2)
    v.tube(shift((310, 720), dz), shift((250, 530), dz), 95, C_KID)
    v.tube(shift((250, 525), dz), shift((60, 520), dz), 70, C_KID)
    v.tube(shift((60, 515), dz), shift((-60, 495), dz), 55, C_KID)
    return H, HB


def _saddle_poly(v, bottom, up, fw, largo, sz, side, dz):
    """contorno lateral de un soporte con silla (side=+1 silla hacia adelante (fw), -1 hacia atrás)."""
    t = P.TUBO_CUADRADO
    tx = G.SADDLE_OFFSET
    hx = 22
    loc = [(-hx * side, 0), (-hx * side, largo), (hx * side, largo), (hx * side, sz + t / 2 + 8),
           ((tx + t / 2 + 7) * side, sz + t / 2 + 8), ((tx + t / 2 + 7) * side, sz - t / 2 - 8),
           (hx * side, sz - t / 2 - 8), (hx * side, 0)]
    pts = [(bottom[0] + fw[0] * x + up[0] * z, bottom[1] + fw[1] * x + up[1] * z + dz) for x, z in loc]
    v.poly(pts, stroke=C_RUN, fill="#ffcc80", w=0.3)
    pin = (bottom[0] + fw[0] * tx * side + up[0] * sz, bottom[1] + fw[1] * tx * side + up[1] * sz + dz)
    return pin


def _fork(v, T, A, rot):
    v.tube(T, A, P.PLETINA_ANCHO, C_STEEL)
    sq = P.TUBO_CUADRADO / 2
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    v.poly([(T[0] + x * c - z * s_, T[1] + x * s_ + z * c) for x, z in ((-sq, -sq), (sq, -sq), (sq, sq), (-sq, sq))],
           stroke="#222", fill="#bdbdbd", w=0.2)
    u = ((A[0] - T[0]), (A[1] - T[1]))
    n = math.hypot(*u)
    u = (u[0] / n, u[1] / n)
    tip = (T[0] + u[0] * 70, T[1] + u[1] * 70)
    v.poly([(T[0] - 17, T[1] - 17), (T[0] + 17, T[1] - 17), (T[0] + 17, T[1] + 17), (T[0] - 17, T[1] + 17)], stroke=C_RUN, fill="none", w=0.25)
    v.tube(T, tip, 30, "#ffcc80")
    for d in (30, 66):
        v.circle((T[0] + u[0] * d, T[1] + u[1] * d), 5, stroke="#222", fill="#9e9e9e", w=0.12)


def eva_wheel(v, c):
    wheel(v, c, G.RN, tire=48, color=C_RUN, spokes=6)


def running_kit_side(v, dz):
    rb = G.REAR_LEG_BOT
    pin_r = _saddle_poly(v, rb, G.REAR_UP, G.REAR_FWD, G.REAR_BRACKET_LEN, G.REAR_SADDLE_Z, -1, dz)
    pin_f = _saddle_poly(v, G.FRONT_BRACKET_BOTTOM, G.FRONT_UP, G.FRONT_FWD, G.FRONT_BRACKET_LEN, G.FRONT_SADDLE_Z, +1, dz)
    A = shift(G.REAR_AXLE, dz)
    B = shift(G.REAR_BEAM, dz)
    T = shift(G.TRAVESANO, dz)
    FA = shift(G.FRONT_AXLE, dz)
    eva_wheel(v, A)
    _fork(v, B, A, -P.PATA_TRASERA_ANGULO)
    eva_wheel(v, FA)
    _fork(v, T, FA, P.PATA_DELANTERA_ANGULO)
    for p in (pin_r, pin_f):
        v.circle(p, 5, stroke="#b71c1c", fill="#e53935", w=0.15)
    return A, FA, T, B


def board_side(v, dz=0.0):
    """patineta + sillín. Devuelve puntos útiles."""
    lat, n, tilt, theta = X._arm_geometry()
    piv = G.from_rear_local((-(22 + 14), G.REAR_BRACKET_LEN + 5 + 40))
    piv = shift(piv, dz)
    deck_bot = P.RUEDITA_DIAM / 2 + (P.RUEDITA_DIAM / 2 + 6 + 8)
    deck_top = deck_bot + P.TABLA_ALTO
    king_x = piv[0] + X.ARM_ADELANTE
    cx = king_x + (P.TABLA_FONDO / 2 - 40)
    x0, x1 = cx - P.TABLA_FONDO / 2, cx + P.TABLA_FONDO / 2
    # abrazadera pivote
    L0 = G.REAR_BRACKET_LEN + 5
    loc = [(22, L0), (22, L0 + 80), (-22, L0 + 80), (-50, L0 + 55), (-50, L0 + 25), (-22, L0)]
    v.poly([shift(G.from_rear_local(q), dz) for q in loc], stroke=C_BOARD, fill="#bbdefb", w=0.3)
    # ruedas y horquillas
    wx = cx + 100
    v.poly([(wx - 30, deck_bot), (wx + 30, deck_bot), (wx + 13, P.RUEDITA_DIAM / 2), (wx - 13, P.RUEDITA_DIAM / 2)], stroke=C_BOARD, fill="#bbdefb", w=0.25)
    wheel(v, (wx, P.RUEDITA_DIAM / 2), P.RUEDITA_DIAM / 2, tire=10, color=C_BOARD)
    # tabla
    v.poly([(x0 + 20, deck_bot), (x1 - 20, deck_bot), (x1, deck_bot + 8), (x1, deck_top), (x0, deck_top), (x0, deck_bot + 8)], stroke=C_BOARD, fill="#90caf9", w=0.3)
    v.line((x0 + 10, deck_top + 2), (x1 - 10, deck_top + 2), "#212121", 0.35)  # lija
    # pivote + yugo
    yz = deck_top + 10 + 38
    v.rect(king_x - 35, deck_top, king_x + 35, deck_top + 10, stroke=C_BOARD, fill="#bbdefb", w=0.2)
    v.poly([(king_x - 26, deck_top + 10), (king_x + 26, deck_top + 10), (king_x + 13, yz + 13), (king_x - 13, yz + 13)], stroke=C_BOARD, fill="#bbdefb", w=0.2)
    v.tube(piv, (king_x - 10, yz), P.BRAZO_TUBO, "#90a4ae")
    v.circle(piv, 8, stroke="#222", fill="#9e9e9e", w=0.15)
    v.circle((king_x, yz), 6, stroke="#222", fill="#9e9e9e", w=0.15)
    # sillín
    seat_z = 360.0
    v.rect(cx - 12, deck_top, cx + 12, deck_top + 78, stroke=C_BOARD, fill="#bbdefb", w=0.2)
    v.tube((cx, deck_top + 20), (cx, seat_z - 16), P.POSTE_ASIENTO, "#90a4ae")
    v.poly([(cx - 105, seat_z), (cx + 105, seat_z), (cx + 95, seat_z - 16), (cx - 95, seat_z - 16)], stroke=C_BOARD, fill="#64b5f6", w=0.3)
    return dict(piv=piv, cx=cx, x0=x0, x1=x1, deck_top=deck_top, seat_z=seat_z, king=(king_x, yz), wheel=wx)


def hammock_and_kid(v, b, H, HB):
    cx, sz = b["cx"], b["seat_z"]
    # anclaje superior en el tubo del manillar
    za = 880.0   # anclaje en el tubo recto del manillar (prolongación de la pata delantera)
    TA = (G.FRONT_LEG_BOT[0] + G.FRONT_UP[0] * (za - G.FRONT_LEG_BOT[1]) / G.FRONT_UP[1], za)
    v.circle(TA, 22, stroke=C_HAM, fill="#a5d6a7", w=0.3)
    # niña de 4 años dormida, mirando hacia el adulto (hacia atrás)
    v.tube((cx - 25, sz + 30), (cx - 165, sz + 330), 120, C_KID)          # torso reclinado
    v.circle((cx - 215, sz + 435), 75, stroke="#c8a58c", fill=C_KID, w=0.2)  # cabeza
    v.circle((cx - 150, sz + 460), 7, stroke="#5d4037", fill="#5d4037", w=0.1)  # ojo (mira al adulto)
    v.tube((cx, sz + 30), (cx + 135, sz + 55), 85, C_KID)                   # muslo
    v.tube((cx + 140, sz + 50), (cx + 150, b["deck_top"] + 25), 65, C_KID)   # pierna
    v.tube((cx - 140, sz + 290), (cx + 20, sz + 190), 45, C_KID)               # brazo
    # lona de la hamaca: desde el anclaje, por detrás de la espalda, bajo el sillín
    v.path([("M", [TA[0], TA[1]]), ("C", [TA[0] + 10, TA[1] - 30, cx - 320, sz + 540, cx - 295, sz + 430]),
            ("C", [cx - 270, sz + 300, cx - 130, sz + 60, cx - 90, sz + 5]),
            ("L", [cx + 100, sz + 3])], stroke=C_HAM, w=1.6)
    # cinta inferior al pivote de la pata
    v.line((cx - 95, sz - 5), b["piv"], C_HAM, 0.5, dash="1.2,0.6")
    # cinturón
    v.line((cx - 95, sz + 140), (cx + 10, sz + 120), C_HAM, 0.6)
    return TA


def tray_side(v, HB):
    bx, bz = HB
    rear = bx - 20
    front = rear - (P.TABLET_FONDO + 30)
    zb = bz + 26
    v.rect(front, zb, rear, zb + 14, stroke=C_TRAY, fill="#e1bee7", w=0.3)
    v.poly([(bx - 22, bz - 20), (bx + 22, bz - 20), (bx + 22, zb), (bx - 70, zb), (bx - 70, zb - 8), (bx - 22, bz + 5)], stroke=C_TRAY, fill="#ce93d8", w=0.2)
    cxm = (front + rear) / 2
    v.rect(cxm - 44, zb + 14 - 75, cxm + 44, zb + 14, stroke=C_TRAY, fill="none", w=0.25, dash="1,0.6")
    # tablet de pie en el riel
    v.poly([(front + 16, zb + 14), (front + 26, zb + 14), (front + 110, zb + 175), (front + 100, zb + 180)], stroke="#212121", fill="#424242", w=0.2)
    return front, rear, zb


# ===========================================================================
def build():
    W, Hh = 420, 297
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{Hh}mm" viewBox="0 0 {W} {Hh}" font-family="Helvetica, Arial, sans-serif">')
    add('<defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">'
        '<path d="M0,2 L10,5 L0,8 z" fill="#333"/></marker>'
        '<pattern id="mesh" width="2" height="2" patternUnits="userSpaceOnUse"><path d="M0,0 L2,2 M2,0 L0,2" stroke="#b0bec5" stroke-width="0.12"/></pattern></defs>')
    add(f'<rect width="{W}" height="{Hh}" fill="white"/>')
    add(f'<rect x="5" y="5" width="{W-10}" height="{Hh-10}" fill="none" stroke="#222" stroke-width="0.5"/>')

    # ---------------- VISTA 1: lateral modo trote
    dz = P.ELEVACION
    v1 = View(60, 138)
    v1.line((-460, 0), (1050, 0), "#9e9e9e", 0.4)
    H, HB = stroller_side(v1, dz, orig_dash=True)
    A, FA, T, B = running_kit_side(v1, dz)
    v1.line((P.MANILLAR_X, P.MANILLAR_Z + dz), (P.MANILLAR_X + 120, P.MANILLAR_Z + dz - 220), "#fb8c00", 0.35, dash="0.8,0.5")
    v1.text((858, 830), "correa de", C_RUN, 2.2, "end")
    v1.text((858, 795), "muñeca", C_RUN, 2.2, "end")
    v1.text((-440, 1230), "1 · VISTA LATERAL — MODO TROTE (3 ruedas)", "#111", 4, weight="bold")
    v1.text((-440, 1170), "patineta, hamaca y bandeja desmontadas", "#555", 2.4)
    v1.text((-440, 1120), "ruedas originales quedan en el aire", "#555", 2.4)
    v1.callout(shift(G.REAR_BRACKET_CENTER, dz), (900, 680), "soporte con silla", C_RUN)
    v1.text((908, 640), "(fijo en el coche)", C_RUN, 2.3)
    v1.callout(B, (900, 560), "pasador de bola", "#c62828")
    v1.text((908, 520), "= enclachar módulo", "#c62828", 2.3)
    v1.callout(((B[0] + A[0]) / 2, (B[1] + A[1]) / 2), (900, 420), "horquilla 2 pletinas", C_STEEL)
    v1.callout((A[0] + 100, A[1] + 100), (900, 300), 'rueda EVA 12" maciza', C_RUN)
    v1.callout(shift(G.REAR_HUB, dz), (900, 150), "rueda original", "#78909c")
    v1.text((908, 110), "(en el aire)", "#78909c", 2.3)
    v1.callout(shift(G.FRONT_BRACKET_CENTER, dz), (-280, 780), "soporte travesaño", C_RUN, "end")
    v1.text((-288, 740), "(impreso)", C_RUN, 2.3, "end")
    v1.callout(T, (-280, 670), "travesaño + pasador", C_STEEL, "end")
    v1.callout(((T[0] + FA[0]) / 2, (T[1] + FA[1]) / 2), (-280, 570), "horquilla 2", C_STEEL, "end")
    v1.text((-288, 530), "pletinas 30x5", C_STEEL, 2.3, "end")
    v1.callout(FA, (-280, 440), 'rueda EVA 12" fija', C_RUN, "end")
    v1.dim((FA[0], 0), (A[0], 0), -120, f"entre ejes {A[0]-FA[0]:.0f}  ·  largo total {P.MANILLAR_X + 16 - FA[0] + G.RN:.0f}")
    v1.dim((870, 0), (870, P.MANILLAR_Z + dz + 16), 0, f"altura manillar {P.MANILLAR_Z + dz + 16:.0f}", vertical=True)
    v1.dim((G.REAR_HUB[0] - 150, 0), (G.REAR_HUB[0] - 150, dz), 0, f"{dz:.0f}", vertical=True)

    # ---------------- VISTA 2: lateral modo paseo
    v2 = View(232, 138)
    v2.line((-150, 0), (1700 - 450, 0), "#9e9e9e", 0.4)
    H2, HB2 = stroller_side(v2, 0)
    b = board_side(v2)
    TA = hammock_and_kid(v2, b, H2, HB2)
    tf, tr, tz = tray_side(v2, HB2)
    v2.text((640, 1250), "2 · VISTA LATERAL — MODO PASEO", "#111", 4, weight="bold")
    v2.text((640, 1190), "patineta + sillín + hamaca (siesta) + bandeja", "#555", 2.4)
    L = 1180
    v2.callout((tf + 60, tz + 14), (L, 1100), "bandeja tablet + 2 portavasos", C_TRAY)
    v2.callout((tf + 70, tz + 110), (L, 1020), "tablet en el riel", "#424242")
    v2.callout(TA, (L, 940), "anclaje superior hamaca", C_HAM)
    v2.callout((b["cx"] - 275, b["seat_z"] + 330), (L, 860), "lona hamaca (respaldo)", C_HAM)
    v2.callout((b["cx"] - 40, b["seat_z"] + 135), (L, 780), "cinturón", C_HAM)
    v2.callout((b["cx"] + 60, b["seat_z"] - 8), (L, 690), "sillín regulable", C_BOARD)
    v2.callout(b["piv"], (L, 600), "abrazadera pivote + anclaje inf.", C_BOARD)
    v2.callout(((b["piv"][0] + b["king"][0]) / 2, (b["piv"][1] + b["king"][1]) / 2), (L, 510), "brazos alu Ø20", "#78909c")
    v2.callout(b["king"], (L, 420), "pivote giratorio M10 + bisagra M8", C_BOARD)
    v2.callout((b["x1"] - 40, b["deck_top"]), (L, 330), "tabla 400x300 (4 baldosas)", C_BOARD)
    v2.callout((b["wheel"], 40), (L, 240), "ruedas patín 80 mm", C_BOARD)
    v2.dim((-G.RF0, 0), (b["x1"], 0), -120, f"largo total {b['x1'] + G.RF0:.0f}")
    v2.dim((b["x0"], 0), (b["x1"], 0), -50, f"{P.TABLA_FONDO:.0f}")
    v2.dim((b["x1"] + 25, 0), (b["x1"] + 25, b["deck_top"]), 0, f"{b['deck_top']:.0f}", vertical=True)
    v2.dim((b["x1"] + 85, 0), (b["x1"] + 85, b["seat_z"]), 0, f"sillín {b['seat_z']:.0f}", vertical=True)
    v2.dim((-180, 0), (-180, P.MANILLAR_Z + 16), 0, f"manillar {P.MANILLAR_Z + 16:.0f}", vertical=True)

    # ---------------- VISTA 3: planta modo paseo  (x igual que vista 2, y lateral hacia abajo)
    v3 = View(238, 214)
    yW = P.ANCHO_CHASIS / 2
    leg = yW - P.PATA_TRASERA_ANCHO / 2
    v3.text((-150, 300), "3 · PLANTA — MODO PASEO", "#111", 3.4, weight="bold")
    # coche (planta)
    legY = G.LEG_Y
    top = handle_points()
    v3.rect(60, -190, 400, 190, stroke=C_SOFT, fill="url(#mesh)", w=0.2)
    for s in (1, -1):
        v3.tube((G.FRONT_LEG_BOT[0], s * legY), (top[0], s * legY))
        v3.tube((G.REAR_LEG_BOT[0], s * legY), (G.HINGE[0], s * legY))
        v3.path([("M", [top[0], s * legY]), ("C", [top[0] + 120, s * (legY + 15), P.MANILLAR_X - 20, s * (yW - 5), P.MANILLAR_X, s * (yW - 40)])], stroke="#8d5524", w=3.0)
        v3.rect(-G.RF0, s * P.RUEDAS_DELANTERAS_ORIG_Y - 18, G.RF0, s * P.RUEDAS_DELANTERAS_ORIG_Y + 18, stroke=C_FRAME, fill="#263238", w=0.2)
        v3.rect(G.REAR_HUB[0] - G.RR0, s * P.RUEDAS_TRASERAS_ORIG_Y - 18, G.REAR_HUB[0] + G.RR0, s * P.RUEDAS_TRASERAS_ORIG_Y + 18, stroke=C_FRAME, fill="#263238", w=0.2)
        v3.tube((G.REAR_LEG_BOT[0], s * legY), (G.REAR_HUB[0], s * (P.RUEDAS_TRASERAS_ORIG_Y - 30)), 20, "#37474f")
    v3.tube((G.REAR_HUB[0], -P.RUEDAS_TRASERAS_ORIG_Y), (G.REAR_HUB[0], P.RUEDAS_TRASERAS_ORIG_Y), 20, "#37474f")
    v3.tube((P.MANILLAR_X, -(yW - 40)), (P.MANILLAR_X, yW - 40), 30, "#8d5524")
    v3.rect(P.MANILLAR_X - 45, -P.MANILLAR_BOTON_ANCHO / 2, P.MANILLAR_X - 10, P.MANILLAR_BOTON_ANCHO / 2, stroke="#222", fill="#37474f", w=0.2)
    v3.rect(-100, -165, 280, 165, stroke="#2e5d4f", fill="#4f7f6f", w=0.25)
    v3.path([("M", [300, -215]), ("C", [420, -235, 540, -230, 560, -200]), ("L", [560, 200]), ("C", [540, 230, 420, 235, 300, 215]), ("Z", [])], stroke="#2e5d4f", fill="#3f6b5d", w=0.25)
    v3.tube((-30, -yW + 15), (-30, yW - 15), 22, "#8d5524")
    # hamaca
    v3.poly([(TA[0], -yW + 15), (TA[0], yW - 15), (b["cx"] - 60, 190), (b["cx"] - 60, -190)], stroke=C_HAM, fill="#c8e6c9", w=0.3, dash="1,0.5")
    # patineta
    lat, n, tilt, theta = X._arm_geometry()
    leg = G.LEG_Y
    for s in (1, -1):
        v3.tube((b["piv"][0], s * (leg - 16)), (b["king"][0] - 25, s * 18), P.BRAZO_TUBO, "#90a4ae")
        v3.rect(b["piv"][0] - 35, s * (leg - 25), b["piv"][0] + 35, s * (leg + 25), stroke=C_BOARD, fill="#bbdefb", w=0.25)
    v3.path([("M", [b["x0"] + 40, -200]), ("L", [b["x1"] - 40, -200]), ("Q", [b["x1"], -200, b["x1"], -160]), ("L", [b["x1"], 160]),
             ("Q", [b["x1"], 200, b["x1"] - 40, 200]), ("L", [b["x0"] + 40, 200]), ("Q", [b["x0"], 200, b["x0"], 160]),
             ("L", [b["x0"], -160]), ("Q", [b["x0"], -200, b["x0"] + 40, -200]), ("Z", [])], stroke=C_BOARD, fill="#90caf9", w=0.3)
    v3.line((b["cx"], -200), (b["cx"], 200), "#64b5f6", 0.15, dash="1,0.6")
    v3.line((b["x0"], 0), (b["x1"], 0), "#64b5f6", 0.15, dash="1,0.6")
    for s in (1, -1):
        v3.rect(b["wheel"] - 40, s * (P.TABLA_ANCHO / 2 - 45) - 12, b["wheel"] + 40, s * (P.TABLA_ANCHO / 2 - 45) + 12, stroke=C_BOARD, fill="#263238", w=0.2)
    v3.circle(b["king"], 26, stroke=C_BOARD, fill="#bbdefb", w=0.3)
    add(f'<ellipse cx="{v3.p(b["cx"], 0)[0]:.2f}" cy="{v3.p(b["cx"], 0)[1]:.2f}" rx="8.5" ry="10.5" stroke="{C_BOARD}" fill="#64b5f6" stroke-width="0.3"/>')
    # bandeja
    tw = P.TABLET_ANCHO + 10
    v3.rect(tf, -tw / 2, tr, tw / 2, stroke=C_TRAY, fill="#e1bee7", w=0.3)
    add('<g opacity="0.85"/>')
    v3.rect(tf + 8, -P.TABLET_ANCHO / 2 + 5, tf + 8 + P.TABLET_FONDO * 0.95, P.TABLET_ANCHO / 2 - 5, stroke="#9e9e9e", fill="none", w=0.15, dash="0.8,0.5")
    cupc = tw / 2 - 12 + 12 + P.VASO_DIAM / 2 + 4
    for s in (1, -1):
        v3.circle(((tf + tr) / 2, s * cupc), P.VASO_DIAM / 2 + 3, stroke=C_TRAY, fill="#ce93d8", w=0.3)
        v3.circle(((tf + tr) / 2, s * cupc), P.VASO_DIAM / 2 - 4, stroke=C_TRAY, fill="white", w=0.2)
    v3.dim((b["x1"], -200), (b["x1"], 200), 60, f"{P.TABLA_ANCHO:.0f}", vertical=True)
    v3.dim((-G.RF0, -yW), (-G.RF0, yW), -60, f"ancho {P.ANCHO_CHASIS:.0f}", vertical=True)

    # ---------------- VISTA 4: trasera modo trote
    hy = 25
    v4 = View(112, 278)
    v4.text((-1000, 1020), "4 · VISTA TRASERA", "#111", 3.4, weight="bold")
    v4.text((-1000, 970), "MODO TROTE", "#111", 3.4, weight="bold")
    v4.line((-460, 0), (460, 0), "#9e9e9e", 0.4)
    zH = G.HINGE[1] + dz
    zbr0 = G.REAR_LEG_BOT[1] + dz
    zb = G.REAR_BEAM[1] + dz
    YW = G.REAR_WHEEL_Y
    half_beam = YW + P.BUJE_ANCHO / 2 + P.PLETINA_ESPESOR + 8
    v4.rect(-half_beam, zb - 10, half_beam, zb + 10, stroke="#222", fill="#bdbdbd", w=0.2)
    leg = G.LEG_Y
    # conjunto trasero original (angosto, con resortes y freno central)
    v4.tube((-leg, zbr0), (leg, zbr0), 22, "#37474f")
    for s_ in (1, -1):
        v4.tube((s_ * 110, zbr0), (s_ * 110, G.RR0 + dz + 25), 22, "#37474f")
        v4.poly([(s_ * 98, G.RR0 + dz + 55), (s_ * 122, G.RR0 + dz + 45), (s_ * 98, G.RR0 + dz + 35), (s_ * 122, G.RR0 + dz + 25)], stroke="#b0bec5", fill="none", w=0.3, close=False)
        yo = s_ * P.RUEDAS_TRASERAS_ORIG_Y
        v4.rect(yo - 18, dz, yo + 18, dz + 2 * G.RR0, stroke=C_FRAME, fill="none", w=0.25, dash="1,0.8")
    v4.tube((-P.RUEDAS_TRASERAS_ORIG_Y + 18, G.RR0 + dz), (P.RUEDAS_TRASERAS_ORIG_Y - 18, G.RR0 + dz), 18, "#37474f")
    v4.rect(-22, G.RR0 + dz + 5, 22, G.RR0 + dz + 30, stroke="#222", fill="#263238", w=0.15)
    for s_ in (1, -1):
        y = s_ * leg
        v4.tube((y, zbr0), (y, zH))
        v4.tube((y, zH), (s_ * (yW - 5), P.MANILLAR_Z + dz))
        v4.rect(y - hy, zbr0, y + hy, zbr0 + G.REAR_BRACKET_LEN * math.cos(math.radians(P.PATA_TRASERA_ANGULO)), stroke=C_RUN, fill="#ffcc80", w=0.3)
        v4.circle((y, zb), 5, stroke="#b71c1c", fill="#e53935", w=0.15)
        yw = s_ * YW
        for e in (-1, 1):
            yp = yw + e * (P.BUJE_ANCHO / 2 + P.PLETINA_ESPESOR / 2)
            v4.rect(yp - 2.5, G.RN - 15, yp + 2.5, zb + 12, stroke="#263238", fill=C_STEEL, w=0.15)
        v4.rect(yw - P.BUJE_ANCHO / 2, zb - 17, yw + P.BUJE_ANCHO / 2, zb + 17, stroke=C_RUN, fill="#ffcc80", w=0.2)
        v4.rect(yw - P.RUEDA_RUNNING_ANCHO / 2, 0, yw + P.RUEDA_RUNNING_ANCHO / 2, 2 * G.RN, stroke=C_RUN, fill="#455a64", w=0.3)
        v4.rect(yw - P.BUJE_ANCHO / 2 - 9, G.RN - 6, yw + P.BUJE_ANCHO / 2 + 9, G.RN + 6, stroke="#222", fill="#9e9e9e", w=0.12)
    v4.tube((-yW + 5, P.MANILLAR_Z + dz), (yW - 5, P.MANILLAR_Z + dz), 30, "#8d5524")
    v4.rect(-P.MANILLAR_BOTON_ANCHO / 2, P.MANILLAR_Z + dz - 18, P.MANILLAR_BOTON_ANCHO / 2, P.MANILLAR_Z + dz + 12, stroke="#222", fill="#37474f", w=0.2)
    v4.rect(-165, 470 + dz, 165, 900 + dz, stroke="#2e5d4f", fill="#4f7f6f", w=0.25)
    v4.path([("M", [-215, 840 + dz]), ("C", [-215, 1060 + dz, 215, 1060 + dz, 215, 840 + dz]), ("Z", [])], stroke="#2e5d4f", fill="#3f6b5d", w=0.25)
    v4.rect(-200, 200 + dz, 200, 400 + dz, stroke=C_SOFT, fill="url(#mesh)", w=0.25)
    v4.dim((-YW, 0), (YW, 0), -70, f"trocha {2*YW:.0f}  ·  ancho total {2*half_beam:.0f}")
    v4.callout((-leg, zb), (-560, 760), "pasador de bola", "#c62828", "end")
    v4.callout((-YW - P.BUJE_ANCHO / 2 - 3, zb - 80), (-560, 660), "módulo trasero:", C_STEEL, "end")
    v4.text((-568, 615), "travesaño + 2 horquillas", C_STEEL, 2.3, "end")
    v4.callout((-YW, G.RN - 100), (-560, 470), 'rueda EVA 12"', C_RUN, "end")
    v4.callout((-P.RUEDAS_TRASERAS_ORIG_Y, dz + 150), (-560, 330), "ruedas originales (aire)", "#78909c", "end")
    v4.callout((0, G.RR0 + dz + 20), (-560, 220), "freno original + resortes", "#37474f", "end")

    # ---------------- notas + rótulo
    nx, ny = 158, 178
    notas = [
        "NOTAS",
        "• Escala 1:10 en hoja A3. Medidas en mm.",
        "• Geometría del Leona 2 calibrada con fotos + ficha",
        "  (85,5 x 47 x 103,5 cm). Confirmar con huincha las",
        "  medidas [MEDIR] de cad/params.py antes de imprimir.",
        "• Naranjo = impreso · gris azulado = acero/alu · rojo = pasador",
        "• Azul = patineta · verde = hamaca · morado = bandeja",
        "• Módulos de ruedas: se enclachan con 4 pasadores de bola.",
        "• Trote: patineta y hamaca SIEMPRE desmontadas.",
        "• Paseo: la patineta funciona con ruedas originales o",
        "  con el kit running puesto (no se tocan).",
        "• Hamaca: la niña va sentada en el sillín mirando hacia",
        "  el adulto; la lona sólo sostiene espalda y cabeza.",
    ]
    for i, t in enumerate(notas):
        add(f'<text x="{nx}" y="{ny + i * 3.4:.1f}" font-size="{3 if i == 0 else 2.15}" font-weight="{"bold" if i == 0 else "normal"}" fill="#333">{t}</text>')
    # leyenda colores
    ly = ny + len(notas) * 3.4 + 2
    for i, (c, t) in enumerate([(C_RUN, "kit running (impreso)"), (C_STEEL, "acero / aluminio"), (C_BOARD, "patineta + sillín"), (C_HAM, "hamaca"), (C_TRAY, "bandeja")]):
        add(f'<rect x="{nx}" y="{ly + i * 4.2}" width="4" height="3" fill="{c}"/><text x="{nx + 5.5}" y="{ly + 2.6 + i * 4.2}" font-size="2.3" fill="#333">{t}</text>')
    # rótulo
    rx, ry = 300, 256
    add(f'<rect x="{rx}" y="{ry}" width="{W - 5 - rx}" height="{Hh - 5 - ry}" fill="white" stroke="#222" stroke-width="0.4"/>')
    add(f'<text x="{rx + 3}" y="{ry + 7}" font-size="4.2" font-weight="bold">PLANO GENERAL</text>')
    add(f'<text x="{rx + 3}" y="{ry + 13}" font-size="2.8">Patineta hermano + kit running + hamaca + bandeja</text>')
    add(f'<text x="{rx + 3}" y="{ry + 18}" font-size="2.8">Coche: Maxi-Cosi Leona 2</text>')
    add(f'<line x1="{rx}" y1="{ry + 21}" x2="{W - 5}" y2="{ry + 21}" stroke="#222" stroke-width="0.3"/>')
    add(f'<text x="{rx + 3}" y="{ry + 26}" font-size="2.6">Escala 1:10 · A3 · mm · generado por cad/plano.py</text>')
    add(f'<text x="{rx + 3}" y="{ry + 30.5}" font-size="2.6">Rueda EVA 12" Ø{P.RUEDA_RUNNING_DIAM:.0f} · elevación {P.ELEVACION:.0f} · eje M{P.EJE_RUEDA:.0f}</text>')
    # regla de escala
    sx, sy = 236, 286
    for k in range(6):
        add(f'<rect x="{sx + k * 10}" y="{sy}" width="10" height="1.5" fill="{"#222" if k % 2 == 0 else "white"}" stroke="#222" stroke-width="0.15"/>')
        add(f'<text x="{sx + k * 10}" y="{sy - 1}" font-size="2" text-anchor="middle">{k * 10}</text>')
    add(f'<text x="{sx + 60}" y="{sy - 1}" font-size="2" text-anchor="middle">60 cm</text>')
    add("</svg>")
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "plano_general.svg")
    with open(path, "w") as f:
        f.write("\n".join(out))
    print("ok", path)


if __name__ == "__main__":
    build()
