"""Todas las piezas imprimibles. Cada función devuelve un Manifold ya orientado
para imprimir (cara plana grande sobre la cama)."""
import math

from lib import (M, box, cbox, cyl, cyl_x, cyl_y, hex_nut, hull, rbox, rrect)
from manifold3d import Manifold
import params as P

G = P.HOLGURA_GOMA
PARED = 6.0


# ===========================================================================
#  ABRAZADERA GENÉRICA PARA TUBO OVALADO DEL COCHE
#  Coordenadas locales: tubo del coche a lo largo de Z, X = adelante/atrás,
#  Y = lateral.  Se divide en dos mitades por el plano X=0 y se aprieta con
#  4 pernos M6 a los costados del tubo.
# ===========================================================================
def _leg_core(ancho, fondo, radio, largo):
    cw = fondo + 2 * G          # canal en X
    cd = ancho + 2 * G          # canal en Y
    by = cd / 2 + M[6][0] / 2 + 2.2   # posición Y de los pernos
    hy = by + 7.5                      # semiancho del cuerpo
    hx = cw / 2 + PARED
    core = rbox(2 * hx, 2 * hy, largo, 5)
    canal = Manifold.extrude(rrect(cw, cd, radio + G), largo + 2).translate((0, 0, -1))
    return core, canal, hx, hy, by


def leg_clamp(ancho, fondo, radio, largo, feature=None, feature_side=-1, bolt_z=None, cut_extra=None):
    """Devuelve (mitad_con_feature, mitad_tapa) ya orientadas para imprimir."""
    core, canal, hx, hy, by = _leg_core(ancho, fondo, radio, largo)
    s = feature_side
    big = 400
    half_f = core ^ box(big, big, big).translate((0 if s > 0 else -big, -big / 2, -1))
    half_c = core ^ box(big, big, big).translate((-big if s > 0 else 0, -big / 2, -1))
    if feature is not None:
        half_f = hull(half_f, feature)
    bolt_z = bolt_z or [12, largo - 12]
    d6, nut6, nh6, head6 = M[6]
    holes_f = []
    holes_c = []
    for z in bolt_z:
        for y in (-by, by):
            shaft = cyl_x(2 * big, d6 / 2).translate((0, y, z))
            holes_f.append(shaft)
            holes_c.append(shaft)
            # tuerca cautiva en la mitad con feature, abierta hacia afuera
            nut = hex_nut(nut6, big).rotate((0, 90, 0))  # a lo largo de +X
            if s < 0:
                nut = nut.mirror((1, 0, 0))
            holes_f.append(nut.translate((s * (hx - 4), y, z)))
            # avellanado para la cabeza en la tapa
            head = cyl_x(big, head6 / 2 + 0.3, center=False)
            if s > 0:
                head = head.mirror((1, 0, 0))
            holes_c.append(head.translate((-s * (hx - 3), y, z)))
    from lib import union
    half_f = half_f - canal - union(*holes_f)
    half_c = half_c - canal - union(*holes_c)
    if cut_extra is not None:
        half_f = half_f - cut_extra
    # orientar: cara de corte (X=0) sobre la cama
    def lay(m, side):
        return m.rotate((0, -90 if side > 0 else 90, 0))
    return lay(half_f, s), lay(half_c, -s)


# ---------------------------------------------------------------------------
# KIT RUNNING
# ---------------------------------------------------------------------------
def rear_arm_geometry():
    """Posiciones (locales del soporte) de los 2 pernos M8 del brazo trasero y del eje."""
    import geom
    largo = geom.REAR_BRACKET_LEN
    core, canal, hx, hy, by = _leg_core(P.PATA_TRASERA_ANCHO, P.PATA_TRASERA_FONDO, P.PATA_TRASERA_RADIO, largo)
    ax = geom.to_rear_local(geom.REAR_AXLE)
    p2 = [-hx - 30.0, 12.0]
    for _ in range(20):
        dx, dz = ax[0] - p2[0], ax[1] - p2[1]
        n = math.hypot(dx, dz)
        d = (dx / n, dz / n)
        p1 = (p2[0] - 42 * d[0], p2[1] - 42 * d[1])
        p2[0] += (-hx - 12.0) - p1[0]
    return tuple(p1), tuple(p2), ax, d, hx, hy


def rear_axle_bracket():
    """Soporte del brazo trasero. Abraza la pata trasera apoyado sobre la
    carcasa de la rueda original; atrás lleva 2 pernos M8 donde se atornilla
    el brazo de pletina de acero (por el lado INTERIOR de la pata)."""
    import geom
    largo = geom.REAR_BRACKET_LEN
    p1, p2, ax, d, hx, hy = rear_arm_geometry()
    pad = hull(cyl_y(2 * hy, 13).translate((p1[0], 0, p1[1])),
               cyl_y(2 * hy, 13).translate((p2[0], 0, p2[1])),
               box(1, 2 * hy, 50, True).translate((-hx + 0.5, 0, 25)))
    cut = cyl_y(400, M[8][0] / 2).translate((p1[0], 0, p1[1])) + cyl_y(400, M[8][0] / 2).translate((p2[0], 0, p2[1]))
    a, b = leg_clamp(P.PATA_TRASERA_ANCHO, P.PATA_TRASERA_FONDO, P.PATA_TRASERA_RADIO, largo,
                     feature=pad, feature_side=-1, bolt_z=[74, largo - 11], cut_extra=cut)
    return a, b


def axle_spacer(largo):
    r = P.RUEDA_RUNNING_BUJE / 2
    return cyl(largo, r + 6) - cyl(largo + 2, r + 0.3).translate((0, 0, -1))


def axle_collar():
    """Collarín con prisionero M5: fija la pletina sobre el eje Ø16 (uno a cada lado)."""
    r = P.RUEDA_RUNNING_BUJE / 2
    c = cyl(14, r + 10) - cyl(20, r + 0.25).translate((0, 0, -3))
    c = c - cyl_x(40, M[5][0] / 2, center=False).translate((0, 0, 7))
    n = M[5][1] + 0.4
    c = c - box(4.6, n, 20).translate((r + 3, -n / 2, 7 - n / 2))
    return c


def front_leg_bracket():
    """Abrazadera de pata delantera que sostiene el travesaño cuadrado."""
    largo = 100
    core, canal, hx, hy, by = _leg_core(P.PATA_DELANTERA_ANCHO, P.PATA_DELANTERA_FONDO, P.PATA_DELANTERA_RADIO, largo)
    t = P.TUBO_CUADRADO
    tx = hx + t / 2 + 3
    tz = largo / 2
    boss = box(t + 12, 2 * hy, t + 14, True).translate((tx, 0, tz))
    canal_t = box(t + 0.6, 400, t + 0.6, True).translate((tx, 0, tz))
    lock = cyl(200, M[6][0] / 2, center=True).translate((tx, 0, tz))
    a, b = leg_clamp(P.PATA_DELANTERA_ANCHO, P.PATA_DELANTERA_FONDO, P.PATA_DELANTERA_RADIO, largo,
                     feature=boss, feature_side=+1, cut_extra=canal_t + lock)
    return a, b


def front_geometry():
    rf = P.RUEDA_RUNNING_DIAM / 2
    dx = P.RUEDA_DELANTERA_ADELANTE
    dz = rf - P.TRAVESANO_ALTURA
    lf = math.hypot(dx, dz)
    ang = math.degrees(math.atan2(dz, dx))
    return lf, ang


def fork_spacer():
    """Bloque central: va sobre el travesaño y separa las dos pletinas de la
    horquilla al ancho del buje. Se imprime de lado."""
    lf, ang = front_geometry()
    w = P.BUJE_DELANTERO_ANCHO - 0.5
    t = P.TUBO_CUADRADO
    ux, uz = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    s1, s2 = 30, 66
    tube_block = box(t + 14, w, t + 14, True).rotate((0, -P.PATA_DELANTERA_ANGULO, 0))
    tip = cyl_y(w, 15).translate((ux * (s2 + 4), 0, uz * (s2 + 4)))
    body = hull(tube_block, tip)
    a = -P.PATA_DELANTERA_ANGULO
    body = body - box(t + 0.6, 400, t + 0.6, True).rotate((0, a, 0))
    body = body - cyl(200, M[6][0] / 2, center=True).rotate((0, a, 0))  # perno que atraviesa el tubo
    for s in (s1, s2):
        body = body - cyl_y(400, M[6][0] / 2).translate((ux * s, 0, uz * s))
    # imprimir con una cara lateral sobre la cama
    return body.rotate((90, 0, 0))


def bar_end_cap():
    """Tapón para los extremos del tubo cuadrado (evita cortes)."""
    t = P.TUBO_CUADRADO
    cap = rbox(t + 3, t + 3, 3, 2)
    plug = rbox(t - 3.4, t - 3.4, 12, 1).translate((0, 0, 3))
    return cap + plug


# ---------------------------------------------------------------------------
# PATINETA
# ---------------------------------------------------------------------------
def board_leg_pivot():
    """Abrazadera de pata trasera con pivote M8 para los brazos de la
    patineta y ranura para la cinta inferior de la hamaca."""
    largo = 80
    core, canal, hx, hy, by = _leg_core(P.PATA_TRASERA_ANCHO, P.PATA_TRASERA_FONDO, P.PATA_TRASERA_RADIO, largo)
    px = -(hx + 14)
    pz = largo / 2
    sx = px - 18
    ear = hull(cyl_y(2 * hy, 14).translate((px, 0, pz)),
               box(10, 2 * hy, 28, True).translate((sx, 0, pz)))
    cut = cyl_y(400, M[8][0] / 2).translate((px, 0, pz))
    slot = box(5, P.CINTA + 2, 200, True).translate((sx + 1, 0, pz))
    a, b = leg_clamp(P.PATA_TRASERA_ANCHO, P.PATA_TRASERA_FONDO, P.PATA_TRASERA_RADIO, largo,
                     feature=ear, feature_side=-1, bolt_z=[11, largo - 11], cut_extra=cut + slot)
    return a, b


ARM_ADELANTE = 240.0   # distancia horizontal pivote-pata -> yugo
ARM_CAIDA = 145.0      # diferencia de altura pivote-pata -> pivote yugo


def _arm_geometry():
    lat = P.ANCHO_CHASIS / 2 - P.PATA_TRASERA_ANCHO / 2 - 16
    fwd, drop = ARM_ADELANTE, ARM_CAIDA
    n = math.sqrt(lat ** 2 + fwd ** 2 + drop ** 2)
    tilt = math.degrees(math.asin(lat / n))            # salida del plano del ojo
    phi = math.atan2(drop, fwd)
    theta = math.degrees(math.atan2(lat * math.cos(phi), fwd))  # ángulo en el yugo
    return lat, n, tilt, theta


def arm_end():
    """Terminal del brazo (tubo Ø20) con ojo M8. El ojo se atornilla en la
    cara INTERIOR de la oreja de la abrazadera; el tubo sale inclinado hacia
    el centro. Se imprimen 2 iguales (sirven para ambos lados)."""
    lat, n, tilt, theta = _arm_geometry()
    r = P.BRAZO_TUBO / 2
    sock_l = 45
    t = math.radians(tilt)
    d = (math.cos(t), 0.0, math.sin(t))
    off = 16
    eye = cyl(12, 14)
    neck = hull(eye, cyl(12, 12).translate((off, 0, 0)))
    sock = cyl(sock_l, r + 4.5).rotate((0, 90 - tilt, 0)).translate((off, 0, 6))
    body = neck + sock
    body = body - cyl(sock_l, r + 0.25).rotate((0, 90 - tilt, 0)).translate((off + 6 * d[0], 0, 6 + 6 * d[2]))
    body = body - cyl(40, M[8][0] / 2, center=True)
    pin = 6 + sock_l * 0.65
    body = body - cyl_y(60, M[5][0] / 2).translate((off + pin * d[0], 0, 6 + pin * d[2]))
    return body ^ box(400, 400, 400, True).translate((0, 0, 200))


def yoke():
    """Unión en V de los dos brazos, con lengüeta para el pivote M8."""
    lat, n, tilt, theta = _arm_geometry()
    r = P.BRAZO_TUBO / 2
    sock_l = 45
    zc = r + 4.5
    tongue = box(40, 19.5, 2 * zc, True).translate((-18, 0, zc))
    hub = cbox(30, 34, 2 * zc).translate((6, 0, 0))
    body = hull(tongue, hub)
    for sgn in (1, -1):
        th = math.radians(theta)
        d = (math.cos(th), sgn * math.sin(th))
        body = body + cyl(sock_l, zc).rotate((0, 90, 0)).rotate((0, 0, sgn * theta)).translate((4, 0, zc))
    for sgn in (1, -1):
        th = math.radians(theta)
        d = (math.cos(th), sgn * math.sin(th))
        body = body - cyl(sock_l, r + 0.25).rotate((0, 90, 0)).rotate((0, 0, sgn * theta)).translate((4 + 8 * d[0], 8 * d[1], zc))
        pin = 8 + sock_l * 0.6
        body = body - cyl(60, M[5][0] / 2, center=True).translate((4 + pin * d[0], pin * d[1], zc))
    body = body - cyl_y(40, M[8][0] / 2).translate((-26, 0, zc))
    return body ^ box(400, 400, 400, True).translate((0, 0, 200))


def swivel_block():
    """Gira sobre el perno M10 (pivote vertical) y recibe la lengüeta del
    yugo entre sus dos orejas (pivote M8)."""
    base = cyl(12, 26)
    ears = []
    for y in (-1, 1):
        ears.append(hull(box(36, 10, 1, True).translate((0, y * 15, 12)),
                         cyl_y(10, 13).translate((0, y * 15, 38))))
    body = base + ears[0] + ears[1]
    body = body - cyl(100, M[10][0] / 2, center=True)
    body = body - hex_nut(M[10][1], M[10][2] + 0.5).translate((0, 0, 12 - M[10][2] - 0.5)) if False else body
    body = body - cyl_y(100, M[8][0] / 2).translate((0, 0, 38))
    # hueco para la cabeza del perno M10 (entra desde arriba)
    body = body - cyl(20, M[10][3] / 2 + 0.5).translate((0, 0, 6))
    return body


def kingpin_plate():
    """Placa superior delantera de la tabla: une las 2 baldosas delanteras y
    lleva el perno pivote M10."""
    p = rbox(130, 70, 10, 8)
    p = p - cyl(30, M[10][0] / 2, center=True)
    for x in (-50, 50):
        for y in (-22, 22):
            p = p - cyl(30, M[6][0] / 2, center=True).translate((x, y, 0))
            p = p - cyl(10, M[6][3] / 2 + 0.3).translate((x, y, 6))
    return p


def _deck_holes():
    """Agujeros verticales en coordenadas de la tabla completa
    (X lateral, Y hacia el coche, origen en el centro)."""
    W, D = P.TABLA_ANCHO, P.TABLA_FONDO
    kp_y = D / 2 - 40
    h = []
    # placa pivote
    for x in (-50, 50):
        for y in (-22, 22):
            h.append((x, kp_y + y, 6))
    h.append((0, kp_y, 10))
    # placa central del asiento
    for x in (-45, 45):
        for y in (-45, 45):
            h.append((x, y, 6))
    # soportes de ruedas traseras
    for sx in (-1, 1):
        for y in (-18, 18):
            h.append((sx * (W / 2 - 45), -D / 2 + 50 + y, 6))
    return h


def deck_tile(ix, iy):
    """Baldosa de la tabla (4 en total: ix,iy en {0,1}). Se imprime con la
    cara de pisar sobre la cama y los nervios hacia arriba."""
    W, D, H = P.TABLA_ANCHO, P.TABLA_FONDO, P.TABLA_ALTO
    tw, td = W / 2, D / 2
    x0 = -W / 2 + ix * tw
    y0 = -D / 2 + iy * td
    # contorno global con esquinas redondeadas, recortado a la baldosa
    outline = rbox(W, D, H, 40)
    clip = box(tw, td, H + 2).translate((x0, y0, -1))
    shell = outline ^ clip
    inner = (Manifold.extrude(rrect(W - 8, D - 8, 36), H) ^ clip).translate((0, 0, 5))
    tile = shell - inner
    # nervios
    ribs = []
    nx, ny = 4, 3
    for i in range(1, nx):
        x = x0 + i * tw / nx
        ribs.append(box(3, td, H).translate((x - 1.5, y0, 0)))
    for j in range(1, ny):
        y = y0 + j * td / ny
        ribs.append(box(tw, 3, H).translate((x0, y - 1.5, 0)))
    # paredes de unión (lados interiores) más gruesas
    seam_x = x0 + tw if ix == 0 else x0       # costura vertical (X=0)
    seam_y = y0 + td if iy == 0 else y0       # costura horizontal (Y=0)
    wx = box(7, td, H).translate((seam_x - (7 if ix == 0 else 0), y0, 0))
    wy = box(tw, 7, H).translate((x0, seam_y - (7 if iy == 0 else 0), 0))
    rib = ribs[0]
    for r in ribs[1:] + [wx, wy]:
        rib = rib + r
    tile = tile + (rib ^ outline)
    # pernos de unión M5 entre baldosas
    for k in (0.25, 0.5, 0.78):
        y = y0 + k * td
        tile = tile - cyl_x(40, M[5][0] / 2).translate((0, y, H / 2 + 2))
        x = x0 + k * tw
        tile = tile - cyl_y(40, M[5][0] / 2).translate((x, 0, H / 2 + 2))
    # resaltes y agujeros verticales
    for (x, y, size) in _deck_holes():
        if x0 - 1 < x < x0 + tw + 1 and y0 - 1 < y < y0 + td + 1:
            tile = tile + (cyl(H, M[size][0] / 2 + 5.5).translate((x, y, 0)) ^ outline ^ clip)
    for (x, y, size) in _deck_holes():
        tile = tile - cyl(100, M[size][0] / 2, center=True).translate((x, y, 0))
    # agujeros de drenaje / alivianado en la placa
    return tile.translate((-x0 - tw / 2, -y0 - td / 2, 0))


def wheel_fork():
    """Horquilla fija para rueda de patín 80 mm (M8)."""
    r = P.RUEDITA_DIAM / 2
    gap = P.RUEDITA_ANCHO + 2
    plate_t = 8
    axle_z = r + 6 + plate_t
    side_t = 7
    top = rbox(gap + 2 * side_t, 60, plate_t, 5)
    sides = []
    for s in (-1, 1):
        sides.append(hull(box(side_t, 60, 1).translate((s * (gap / 2 + side_t / 2) - side_t / 2, -30, plate_t - 1)),
                          cyl_x(side_t, 13).translate((s * (gap / 2 + side_t / 2), 0, axle_z))))
    f = top + sides[0] + sides[1]
    f = f - cyl_x(200, M[8][0] / 2).translate((0, 0, axle_z))
    for y in (-18, 18):
        f = f - cyl(30, M[6][0] / 2, center=True).translate((0, y, 0))
    # se imprime con la placa sobre la cama
    return f


def seat_plate():
    """Placa central (une las 4 baldosas) con el zócalo del poste del asiento."""
    r = P.POSTE_ASIENTO / 2 + 0.25
    p = rbox(140, 140, 8, 12)
    sleeve = cyl(78, r + 6)
    gus = []
    for a in (0, 90, 180, 270):
        g = hull(box(30, 5, 1).translate((r, -2.5, 8)), box(1, 5, 40).translate((r + 1, -2.5, 8)))
        gus.append(g.rotate((0, 0, a)))
    p = p + sleeve
    for g in gus:
        p = p + g
    p = p - cyl(100, r).translate((0, 0, 4))
    p = p - cyl_x(100, M[6][0] / 2).translate((0, 0, 60)) - cyl_y(100, M[6][0] / 2).translate((0, 0, 60))
    for x in (-45, 45):
        for y in (-45, 45):
            p = p - cyl(30, M[6][0] / 2, center=True).translate((x, y, 0))
            p = p - cyl(10, M[6][3] / 2 + 0.3).translate((x, y, 4))
    return p


def saddle():
    """Asiento tipo sillín ancho. Se imprime al revés (cara de sentarse en
    la cama). Agujeros para atar la base de la hamaca."""
    from manifold3d import CrossSection
    top = CrossSection.circle(1, 96).scale((105, 85))
    bot = CrossSection.circle(1, 96).scale((95, 75))
    seat = hull(Manifold.extrude(top, 2), Manifold.extrude(bot, 2).translate((0, 0, 16)))
    # vaciar la parte inferior para ahorrar plástico dejando costillas
    hollow = Manifold.extrude(CrossSection.circle(1, 96).scale((88, 68)), 20).translate((0, 0, 6))
    seat = seat - hollow
    r = P.POSTE_ASIENTO / 2 + 0.25
    for a in range(0, 180, 45):
        seat = seat + (box(180, 4, 14, True).rotate((0, 0, a)).translate((0, 0, 13)) ^
                       Manifold.extrude(CrossSection.circle(1, 96).scale((90, 70)), 30))
    sleeve = cyl(60, r + 6).translate((0, 0, 4))
    seat = seat + sleeve - cyl(70, r).translate((0, 0, 10))
    seat = seat - cyl_x(100, M[6][0] / 2).translate((0, 0, 48))
    # ojales para cintas de la hamaca (4)
    for x, y in ((80, 0), (-80, 0), (0, 64), (0, -64)):
        seat = seat - box(6 if x else 26, 26 if x else 6, 60, True).translate((x * 0.95, y * 0.95, 0))
    return seat


# ---------------------------------------------------------------------------
# ABRAZADERA REDONDA GENÉRICA (manillar)
# ---------------------------------------------------------------------------
def round_clamp(diam, alto, tab=None, tab_cut=None):
    ri = diam / 2 + G
    ro = ri + 5
    by = ri + 5
    ring = hull(cbox(24, 2 * by + 14, alto), cyl(alto, ro))
    if tab is not None:
        ring = ring + tab
    ring = ring - cyl(alto + 2, ri).translate((0, 0, -1))
    for y in (-by, by):
        z = alto * 0.5
        ring = ring - cyl_x(100, M[5][0] / 2).translate((0, y, z))
        ring = ring - hex_nut(M[5][1], 50).rotate((0, 90, 0)).translate((6, y, z))
        ring = ring - cyl_x(50, M[5][3] / 2 + 0.3, center=False).mirror((1, 0, 0)).translate((-6, y, z))
    if tab_cut is not None:
        ring = ring - tab_cut
    big = 400
    a = ring ^ box(big, big, big).translate((0, -big / 2, -1))
    b = ring ^ box(big, big, big).translate((-big, -big / 2, -1))
    return a.rotate((0, -90, 0)), b.rotate((0, 90, 0))


def handle_anchor():
    """Anclaje superior de la hamaca en los tubos laterales del manillar."""
    d = P.TUBO_LATERAL_MANILLAR_DIAM
    ri = d / 2 + G
    alto = 40
    tab = hull(cbox(4, 30, alto).translate((ri + 2, 0, 0)), cbox(12, 30, alto).translate((ri + 26, 0, 0)))
    slot = box(5, 40, P.CINTA + 2, True).translate((ri + 25, 0, alto / 2))
    return round_clamp(d, alto, tab=tab, tab_cut=slot)


def tray_bar_clamp():
    """Abrazadera del manillar para la bandeja. Se parte en un plano
    horizontal; la mitad superior lleva la pestaña plana donde se atornilla
    la bandeja (2 x M5)."""
    d = P.MANILLAR_DIAM
    ri = d / 2 + G
    ro = ri + 5
    alto = 30
    bx = ri + 5.5
    body = hull(cyl(alto, ro), cbox(2 * bx + 14, 16, alto))
    tab = box(ro + 6 + 66, 8, alto).translate((-ro - 6, ro - 2, 0))
    body = body + tab + hull(cbox(2 * ro, 1, alto).translate((0, ro - 2, 0)), cbox(2 * bx + 14, 1, alto))
    body = body - cyl(alto + 2, ri).translate((0, 0, -1))
    for x in (-bx, bx):
        body = body - cyl_y(200, M[5][0] / 2).translate((x, 0, alto / 2))
        body = body - hex_nut(M[5][1], 5).rotate((-90, 0, 0)).translate((x, ro + 6 - 4.5, alto / 2))
        body = body - cyl(50, M[5][3] / 2 + 0.3).rotate((90, 0, 0)).translate((x, -6, alto / 2))
    for x in (ro + 18, ro + 48):
        body = body - cyl_y(200, M[5][0] / 2).translate((x, 0, alto / 2))
        body = body - hex_nut(M[5][1], 5).rotate((90, 0, 0)).translate((x, ro - 2 + 4.5, alto / 2))
    big = 400
    top = body ^ box(big, big, big).translate((-big / 2, 0, -1))
    bot = body ^ box(big, big, big).translate((-big / 2, -big, -1))
    # top: cara superior de la pestaña sobre la cama; bot: cara de corte sobre la cama
    return top.rotate((-90, 0, 0)), bot.rotate((90, 0, 0))


# ---------------------------------------------------------------------------
# BANDEJA
# ---------------------------------------------------------------------------
def tray_dims():
    w = P.TABLET_ANCHO + 10
    d = P.TABLET_FONDO + 30
    return w, d


def tray_half(side):
    """Media bandeja (side = -1 izquierda, +1 derecha). Base 4 mm, borde
    10 mm, riel con ranura para dejar la tablet de pie."""
    w, d = tray_dims()
    base_t, rim_h, rim_t = 4, 14, 3
    full = rbox(w, d, rim_h, 10)
    inner = rbox(w - 2 * rim_t, d - 2 * rim_t, rim_h, 8).translate((0, 0, base_t))
    t = full - inner
    # riel para la tablet de pie (lado del coche = +Y)
    rail_y = d / 2 - 22
    rail = box(w - 2 * rim_t, 18, 12, True).translate((0, rail_y, base_t + 6))
    groove = box(w - 40, 12, 20, True).translate((0, rail_y, base_t + 4 + 10))
    t = t + rail - groove
    # nervios de unión en la costura (X=0), bajo la base
    seam = box(10, d - 30, 16, True).translate((0, 0, -8))
    t = t + seam
    for y in (-d / 2 + 35, 0, d / 2 - 35):
        t = t - cyl_x(40, M[4][0] / 2).translate((0, y, -8))
    # agujeros de las abrazaderas del manillar y de los portavasos
    for x in (-90, 90):
        for y in (-d / 2 + 18, -d / 2 + 48):
            t = t - cyl(50, M[5][0] / 2, center=True).translate((x, y, 0))
            t = t - cyl(3, M[5][3] / 2 + 0.3).translate((x, y, base_t - 2.5))
    for sx in (-1, 1):
        for y in (-40, 40):
            t = t - cyl(50, M[4][0] / 2, center=True).translate((sx * (w / 2 - 12), y, 0))
            t = t - cyl(3, M[4][3] / 2 + 0.3).translate((sx * (w / 2 - 12), y, base_t - 2.5))
    # drenaje
    for y in (-50, 50):
        t = t - cyl(20, 3, center=True).translate((side * 30, y, 0))
    big = 400
    if side > 0:
        h = t ^ box(big, big, big).translate((0, -big / 2, -big / 2))
    else:
        h = t ^ box(big, big, big).translate((-big, -big / 2, -big / 2))
    return h


def cup_holder():
    """Portavasos que se atornilla bajo el borde lateral de la bandeja.
    Se imprime boca abajo (pestaña sobre la cama), sin soportes."""
    w, d = tray_dims()
    r = P.VASO_DIAM / 2
    h = 75
    cupc = 12 + r + 4
    body = cyl(h, r + 3)
    body = body + box(cupc + 15, 100, 4).translate((-cupc - 15, -50, h - 4))
    cav = cyl(h - 12, r).translate((0, 0, 12)) + cyl(12, r - 18, r).translate((0, 0, 0)) + cyl(10, r - 18, center=True)
    body = body - cav
    for y in (-40, 40):
        body = body - cyl(50, M[4][0] / 2, center=True).translate((-cupc, y, h))
        body = body - hex_nut(M[4][1], 3.5).translate((-cupc, y, h - 4 - 0.01))
    body = body - box(30, 24, 45, True).translate((r, 0, h - 10))   # asa de tazón
    return body.rotate((180, 0, 0))


def cup_shim(inner_d):
    """Calzo (reductor) para el portavasos. Ideal en TPU."""
    ro = P.VASO_DIAM / 2 - 0.4
    ri = inner_d / 2
    h = 60
    s = cyl(h, ro) + cyl(3, ro + 4).translate((0, 0, h - 3))
    s = s - cyl(h + 2, ri).translate((0, 0, -1))
    for a in (0, 120, 240):
        s = s - box(3, 40, 40, True).translate((0, ro, 20)).rotate((0, 0, a))
    s = s - box(30, 24, 45, True).translate((ro, 0, h - 10))
    return s.rotate((180, 0, 0))


def cup():
    """Vaso de 78 mm (≈350 ml)."""
    ro = 38.5
    h = 110
    c = cyl(h, ro, ro + 2) - cyl(h, ro - 2.2, ro + 2 - 2.2).translate((0, 0, 3))
    return c


# ---------------------------------------------------------------------------
# PIEZAS DE PRUEBA
# ---------------------------------------------------------------------------
def test_ring(ancho, fondo, radio):
    core, canal, hx, hy, by = _leg_core(ancho, fondo, radio, 8)
    return (rbox(fondo + 2 * G + 6, ancho + 2 * G + 6, 8, 4)) - canal


def test_round(d):
    return cyl(8, d / 2 + G + 3) - cyl(10, d / 2 + G).translate((0, 0, -1))
