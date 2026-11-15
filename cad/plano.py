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


def stroller_side(v, dz, orig_dash=False):
    """Maxi-Cosi Leona 2 en vista lateral (geometría estimada)."""
    H = shift(G.HINGE, dz)
    FL = shift(G.FRONT_LEG_BOT, dz)
    RL = shift(G.REAR_LEG_BOT, dz)
    HB = (P.MANILLAR_X, P.MANILLAR_Z + dz)
    dash = "1,0.8" if orig_dash else None
    # cesto
    bk = [(120, 170), (530, 170), (555, 320), (110, 320)]
    v.poly([shift(q, dz) for q in bk], stroke=C_SOFT, fill="url(#mesh)", w=0.25)
    # ruedas originales
    wheel(v, shift(G.FRONT_HUB, dz), G.RF0, color=C_FRAME, dash=dash)
    wheel(v, shift(G.REAR_HUB, dz), G.RR0, color=C_FRAME, dash=dash)
    # horquilla giratoria delantera y carcasa trasera
    v.poly([shift(q, dz) for q in [(-5, 90), (35, 90), (45, 225), (5, 225)]], stroke=C_FRAME, fill="#78909c", w=0.2)
    v.poly([shift(q, dz) for q in [(530, 95), (585, 95), (590, 155), (530, 155)]], stroke=C_FRAME, fill="#78909c", w=0.2)
    v.poly([shift(q, dz) for q in [(585, 140), (630, 135), (632, 150), (588, 155)]], stroke=C_FRAME, fill="#90a4ae", w=0.15)  # freno
    # chasis
    v.tube(FL, H)
    v.tube(RL, H)
    v.tube(H, HB)
    v.circle(HB, 16, stroke=C_FRAME, fill="#37474f", w=0.2)  # manillar con espuma
    # apoyabrazos + barra frontal
    v.tube(H, (H[0] - 190, H[1] + 25), 18)
    v.circle((H[0] - 195, H[1] + 25), 14, stroke=C_FRAME, fill="#37474f", w=0.2)
    # asiento, respaldo, apoyapiés
    v.poly([shift(q, dz) for q in [(110, 470), (385, 440), (395, 470), (130, 500)]], stroke=C_SOFT, fill=C_FAB, w=0.25)
    v.poly([shift(q, dz) for q in [(370, 445), (560, 880), (525, 895), (345, 470)]], stroke=C_SOFT, fill=C_FAB, w=0.25)
    v.poly([shift(q, dz) for q in [(40, 325), (140, 345), (140, 365), (40, 348)]], stroke=C_SOFT, fill=C_FAB, w=0.25)
    v.tube(shift((110, 470), dz), shift((60, 345), dz), 40, C_FAB)  # tela pierna
    # capota
    v.path([("M", [450, 760 + dz]), ("C", [520, 1000 + dz, 260, 1060 + dz, 130, 820 + dz]),
            ("L", [175, 810 + dz]), ("C", [270, 990 + dz, 470, 960 + dz, 415, 765 + dz]), ("Z", [])],
           stroke="#78909c", fill="#b0bec5", w=0.25)
    # bebé (1 año)
    v.circle(shift((420, 760), dz), 62, stroke="#c8a58c", fill=C_KID, w=0.2)
    v.tube(shift((395, 690), dz), shift((300, 520), dz), 95, C_KID)
    v.tube(shift((300, 515), dz), shift((175, 505), dz), 70, C_KID)
    v.tube(shift((175, 500), dz), shift((130, 380), dz), 55, C_KID)
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
    t = 0.68
    TA = (H[0] + (HB[0] - H[0]) * t, H[1] + (HB[1] - H[1]) * t)
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
    # coche
    for s in (1, -1):
        v3.tube((G.FRONT_LEG_BOT[0], s * leg), (G.HINGE[0], s * leg))
        v3.tube((G.REAR_LEG_BOT[0], s * leg), (G.HINGE[0], s * leg))
        v3.tube((G.HINGE[0], s * leg), (P.MANILLAR_X, s * leg))
        v3.rect(-G.RF0, s * leg - 15 * s, G.RF0, s * leg + 25 * s, stroke=C_FRAME, fill="#263238", w=0.2)
        v3.rect(G.REAR_HUB[0] - G.RR0, s * (leg + 8), G.REAR_HUB[0] + G.RR0, s * (leg + 48), stroke=C_FRAME, fill="#263238", w=0.2)
    v3.tube((P.MANILLAR_X, -yW), (P.MANILLAR_X, yW), 30, "#37474f")
    v3.rect(130, -165, 560, 165, stroke=C_SOFT, fill=C_FAB, w=0.25)
    v3.path([("M", [150, -205]), ("C", [300, -240, 430, -240, 470, -205]), ("L", [470, 205]), ("C", [430, 240, 300, 240, 150, 205]), ("Z", [])], stroke="#78909c", fill="#b0bec5", w=0.25)
    v3.tube((G.HINGE[0] - 195, -yW + 10), (G.HINGE[0] - 195, yW - 10), 25, "#37474f")
    # bandeja
    tw = P.TABLET_ANCHO + 10
    v3.rect(tf, -tw / 2, tr, tw / 2, stroke=C_TRAY, fill="#e1bee7", w=0.3)
    v3.rect(tf + 8, -P.TABLET_ANCHO / 2 + 5, tf + 8 + P.TABLET_FONDO * 0.95, P.TABLET_ANCHO / 2 - 5, stroke="#9e9e9e", fill="none", w=0.15, dash="0.8,0.5")
    cupc = tw / 2 - 12 + 12 + P.VASO_DIAM / 2 + 4
    for s in (1, -1):
        v3.circle(((tf + tr) / 2, s * cupc), P.VASO_DIAM / 2 + 3, stroke=C_TRAY, fill="#ce93d8", w=0.3)
        v3.circle(((tf + tr) / 2, s * cupc), P.VASO_DIAM / 2 - 4, stroke=C_TRAY, fill="white", w=0.2)
    # hamaca
    v3.poly([(TA[0], -yW + 15), (TA[0], yW - 15), (b["cx"] - 60, 190), (b["cx"] - 60, -190)], stroke=C_HAM, fill="#c8e6c9", w=0.3, dash="1,0.5")
    # patineta
    lat, n, tilt, theta = X._arm_geometry()
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
    v3.dim((b["x1"], -200), (b["x1"], 200), 60, f"{P.TABLA_ANCHO:.0f}", vertical=True)
    v3.dim((-G.RF0, -yW), (-G.RF0, yW), -60, f"ancho coche {P.ANCHO_CHASIS:.0f}", vertical=True)

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
    for s_ in (1, -1):
        y = s_ * leg
        v4.tube((y, zbr0), (y, zH))
        v4.tube((y, zH), (s_ * (yW - 5), P.MANILLAR_Z + dz))
        v4.rect(s_ * (leg + 8), dz, s_ * (leg + 48), dz + 2 * G.RR0, stroke=C_FRAME, fill="none", w=0.25, dash="1,0.8")
        v4.rect(y - hy, zbr0, y + hy, zbr0 + G.REAR_BRACKET_LEN * math.cos(math.radians(P.PATA_TRASERA_ANGULO)), stroke=C_RUN, fill="#ffcc80", w=0.3)
        v4.circle((y, zb), 5, stroke="#b71c1c", fill="#e53935", w=0.15)
        yw = s_ * YW
        for e in (-1, 1):
            yp = yw + e * (P.BUJE_ANCHO / 2 + P.PLETINA_ESPESOR / 2)
            v4.rect(yp - 2.5, G.RN - 15, yp + 2.5, zb + 12, stroke="#263238", fill=C_STEEL, w=0.15)
        v4.rect(yw - P.BUJE_ANCHO / 2, zb - 17, yw + P.BUJE_ANCHO / 2, zb + 17, stroke=C_RUN, fill="#ffcc80", w=0.2)
        v4.rect(yw - P.RUEDA_RUNNING_ANCHO / 2, 0, yw + P.RUEDA_RUNNING_ANCHO / 2, 2 * G.RN, stroke=C_RUN, fill="#455a64", w=0.3)
        v4.rect(yw - P.BUJE_ANCHO / 2 - 9, G.RN - 6, yw + P.BUJE_ANCHO / 2 + 9, G.RN + 6, stroke="#222", fill="#9e9e9e", w=0.12)
    v4.tube((-yW + 5, P.MANILLAR_Z + dz), (yW - 5, P.MANILLAR_Z + dz), 30, "#37474f")
    v4.rect(-165, 470 + dz, 165, 880 + dz, stroke=C_SOFT, fill=C_FAB, w=0.25)
    v4.path([("M", [-215, 820 + dz]), ("C", [-215, 1060 + dz, 215, 1060 + dz, 215, 820 + dz]), ("Z", [])], stroke="#78909c", fill="#b0bec5", w=0.25)
    v4.rect(-210, 170 + dz, 210, 320 + dz, stroke=C_SOFT, fill="url(#mesh)", w=0.25)
    v4.dim((-YW, 0), (YW, 0), -70, f"trocha {2*YW:.0f}  ·  ancho total {2*half_beam:.0f}")
    v4.callout((-leg, zb), (-560, 760), "pasador de bola", "#c62828", "end")
    v4.callout((-YW - P.BUJE_ANCHO / 2 - 3, zb - 80), (-560, 660), "módulo trasero:", C_STEEL, "end")
    v4.text((-568, 615), "travesaño + 2 horquillas", C_STEEL, 2.3, "end")
    v4.callout((-YW, G.RN - 100), (-560, 470), 'rueda EVA 12"', C_RUN, "end")
    v4.callout((-(leg + 28), dz + 150), (-560, 330), "rueda original (aire)", "#78909c", "end")

    # ---------------- notas + rótulo
    nx, ny = 158, 178
    notas = [
        "NOTAS",
        "• Escala 1:10 en hoja A3. Medidas en mm.",
        "• Geometría del Leona 2 ESTIMADA de la ficha técnica",
        "  (85,5 x 47 x 103,5 cm; ruedas 18 / 21 cm). Medir el",
        "  coche real y corregir cad/params.py antes de imprimir.",
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
