"""Geometría de referencia del coche y posiciones derivadas del kit.
Coordenadas del coche ORIGINAL (sobre sus ruedas): X hacia atrás, Z arriba,
origen en el centro de la rueda delantera original."""
import math
import params as P

RF0 = P.RUEDA_DELANTERA_ORIG / 2
RR0 = P.RUEDA_TRASERA_ORIG / 2
RN = P.RUEDA_RUNNING_DIAM / 2

FRONT_HUB = (0.0, RF0)
REAR_HUB = (P.EJE_TRASERO_ORIG_X, RR0)

b = math.radians(P.PATA_TRASERA_ANGULO)
REAR_UP = (-math.sin(b), math.cos(b))           # dirección "arriba" de la pata trasera
REAR_FWD = (-math.cos(b), -math.sin(b))         # eje X local del soporte (hacia adelante)
REAR_LEG_BOT = (P.PATA_TRASERA_BASE_X, P.PATA_TRASERA_TOPE_Z)

a = math.radians(P.PATA_DELANTERA_ANGULO)
FRONT_UP = (math.sin(a), math.cos(a))            # pata delantera sube hacia atrás
FRONT_LEG_BOT = (20.0, P.PATA_DELANTERA_TOPE_Z)


def on_rear_leg(d):
    return (REAR_LEG_BOT[0] + REAR_UP[0] * d, REAR_LEG_BOT[1] + REAR_UP[1] * d)


def front_leg_at_z(z):
    t = (z - FRONT_LEG_BOT[1]) / FRONT_UP[1]
    return (FRONT_LEG_BOT[0] + FRONT_UP[0] * t, z)


# ---- hinge (bisagra) donde se juntan patas y manillar
def _hinge():
    # intersección pata delantera / pata trasera
    x1, z1 = FRONT_LEG_BOT; dx1, dz1 = FRONT_UP
    x2, z2 = REAR_LEG_BOT; dx2, dz2 = REAR_UP
    det = dx1 * (-dz2) - dz1 * (-dx2)
    t = ((x2 - x1) * (-dz2) - (z2 - z1) * (-dx2)) / det
    return (x1 + dx1 * t, z1 + dz1 * t)


HINGE = _hinge()

# ---- kit running (coordenadas del coche original; en el suelo todo sube ELEVACION)
# Soporte con "silla" en U abierta + pasador. Local: x adelante ⟂ pata, z a lo largo de la pata.
SADDLE_OFFSET = 35.0                       # centro del tubo 20x20 respecto al eje de la pata
REAR_BRACKET_LEN = 120.0
REAR_SADDLE_Z = 80.0                       # el travesaño trasero va alto para pasar SOBRE la rueda original
FRONT_BRACKET_LEN = 100.0
FRONT_SADDLE_Z = 50.0


def to_rear_local(pt):
    vx, vz = pt[0] - REAR_LEG_BOT[0], pt[1] - REAR_LEG_BOT[1]
    return (vx * REAR_FWD[0] + vz * REAR_FWD[1], vx * REAR_UP[0] + vz * REAR_UP[1])


def from_rear_local(p):
    return (REAR_LEG_BOT[0] + REAR_FWD[0] * p[0] + REAR_UP[0] * p[1],
            REAR_LEG_BOT[1] + REAR_FWD[1] * p[0] + REAR_UP[1] * p[1])


REAR_BRACKET_CENTER = from_rear_local((0, REAR_BRACKET_LEN / 2))
REAR_BEAM = from_rear_local((-SADDLE_OFFSET, REAR_SADDLE_Z))
REAR_AXLE = (REAR_HUB[0] + P.EJE_TRASERO_ATRAS, RN - P.ELEVACION)
# rueda trasera nueva por fuera de la original
LEG_Y = P.PATA_SEPARACION / 2
# rueda trasera nueva por fuera de la pata trasera (soporte de 25 mm + 10 de holgura)
REAR_WHEEL_Y = LEG_Y + 25 + 10 + P.PLETINA_ESPESOR + P.BUJE_ANCHO / 2

FRONT_FWD = (-math.cos(a), math.sin(a))          # ⟂ a la pata delantera, hacia adelante


def _travesano():
    zt = P.TRAVESANO_ALTURA - P.ELEVACION
    zl = zt - FRONT_FWD[1] * SADDLE_OFFSET
    lx, lz = front_leg_at_z(zl)
    return (lx + FRONT_FWD[0] * SADDLE_OFFSET, zt), (lx, lz)


TRAVESANO, _FRONT_SADDLE_ON_LEG = _travesano()
FRONT_BRACKET_BOTTOM = (_FRONT_SADDLE_ON_LEG[0] - FRONT_UP[0] * FRONT_SADDLE_Z,
                        _FRONT_SADDLE_ON_LEG[1] - FRONT_UP[1] * FRONT_SADDLE_Z)
FRONT_BRACKET_CENTER = (FRONT_BRACKET_BOTTOM[0] + FRONT_UP[0] * FRONT_BRACKET_LEN / 2,
                        FRONT_BRACKET_BOTTOM[1] + FRONT_UP[1] * FRONT_BRACKET_LEN / 2)
FRONT_AXLE = (TRAVESANO[0] - P.RUEDA_DELANTERA_ADELANTE, RN - P.ELEVACION)


def fork(tube, axle):
    """(largo, ángulo) de la horquilla en coordenadas 'X adelante'."""
    dx = -(axle[0] - tube[0])
    dz = axle[1] - tube[1]
    return math.hypot(dx, dz), math.degrees(math.atan2(dz, dx)), dx, dz


def checks():
    msgs = []
    if FRONT_BRACKET_BOTTOM[1] < P.PATA_DELANTERA_TOPE_Z - 1:
        msgs.append(f"AVISO: el soporte delantero baja hasta z={FRONT_BRACKET_BOTTOM[1]:.0f} y el giratorio llega a "
                    f"{P.PATA_DELANTERA_TOPE_Z:.0f}: sube TRAVESANO_ALTURA.")
    # rueda nueva vs ruedas originales (en planta)
    if REAR_WHEEL_Y - P.RUEDA_RUNNING_ANCHO / 2 < P.RUEDAS_TRASERAS_ORIG_Y + 30:
        msgs.append("AVISO: la rueda trasera nueva queda muy cerca de la original.")
    if REAR_BEAM[1] < REAR_HUB[1] + RR0 + 10 and abs(REAR_BEAM[0] - REAR_HUB[0]) < RR0:
        msgs.append("AVISO: el travesaño trasero roza las ruedas originales.")
    return msgs
