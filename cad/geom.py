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
REAR_LEG_BOT = (P.EJE_TRASERO_ORIG_X, P.PATA_TRASERA_TOPE_Z)

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
REAR_BRACKET_LEN = 110.0
REAR_BRACKET_CENTER = on_rear_leg(REAR_BRACKET_LEN / 2)
REAR_AXLE = (REAR_HUB[0] + P.EJE_TRASERO_ATRAS, RN - P.ELEVACION)


def to_rear_local(pt):
    """coordenadas locales del soporte trasero (x adelante ⟂ pata, z a lo largo de la pata,
    origen en la base del soporte)"""
    vx, vz = pt[0] - REAR_LEG_BOT[0], pt[1] - REAR_LEG_BOT[1]
    return (vx * REAR_FWD[0] + vz * REAR_FWD[1], vx * REAR_UP[0] + vz * REAR_UP[1])


def from_rear_local(p):
    return (REAR_LEG_BOT[0] + REAR_FWD[0] * p[0] + REAR_UP[0] * p[1],
            REAR_LEG_BOT[1] + REAR_FWD[1] * p[0] + REAR_UP[1] * p[1])


FRONT_FWD = (-math.cos(a), math.sin(a))          # ⟂ a la pata, hacia adelante
FRONT_TUBE_OFFSET = 35.0                          # centro del tubo 20x20 delante del eje de la pata


def _travesano():
    zt = P.TRAVESANO_ALTURA - P.ELEVACION
    zl = zt - FRONT_FWD[1] * FRONT_TUBE_OFFSET
    lx, lz = front_leg_at_z(zl)
    return (lx + FRONT_FWD[0] * FRONT_TUBE_OFFSET, zt), (lx, lz)


TRAVESANO, FRONT_BRACKET_CENTER = _travesano()
FRONT_AXLE = (TRAVESANO[0] - P.RUEDA_DELANTERA_ADELANTE, RN - P.ELEVACION)
