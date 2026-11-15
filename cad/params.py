"""
PARÁMETROS DEL PROYECTO  (todas las medidas en milímetros)
===========================================================

ANTES DE IMPRIMIR: mide TU coche con un pie de metro (calibre) y corrige
los valores marcados con  [MEDIR].  Los valores por defecto son estimaciones
para el Maxi-Cosi Leona 2 (no hay planos públicos del chasis).

Después de editar, regenera todo con:   python3 cad/build.py
Y antes de imprimir las piezas grandes imprime  stl/00_pruebas/  para
comprobar el ajuste en el tubo real.
"""

# ---------------------------------------------------------------------------
# Impresora
# ---------------------------------------------------------------------------
CAMA = 220            # lado útil de la cama (Ender 3 = 220, Bambu/Prusa MK4 = 250)

# ---------------------------------------------------------------------------
# Chasis del coche  (Maxi-Cosi Leona 2)
# Los tubos del Leona 2 son ovalados/rectangulares redondeados.
#   ancho  = medida de lado a lado (eje lateral del coche)
#   fondo  = medida de adelante hacia atrás
# ---------------------------------------------------------------------------
PATA_TRASERA_ANCHO = 22.0   # [MEDIR]
PATA_TRASERA_FONDO = 30.0   # [MEDIR]
PATA_TRASERA_RADIO = 8.0    # [MEDIR] radio de las esquinas del óvalo

PATA_DELANTERA_ANCHO = 22.0  # [MEDIR]
PATA_DELANTERA_FONDO = 30.0  # [MEDIR]
PATA_DELANTERA_RADIO = 8.0   # [MEDIR]
PATA_DELANTERA_ANGULO = 12.0 # [MEDIR] inclinación de la pata delantera respecto a la vertical (grados)

MANILLAR_DIAM = 28.0         # [MEDIR] diámetro del manillar CON la espuma
TUBO_LATERAL_MANILLAR_DIAM = 26.0  # [MEDIR] tubos laterales del manillar (anclaje hamaca)

ANCHO_CHASIS = 470.0         # ancho exterior entre patas traseras (ficha: 47 cm)
RUEDA_TRASERA_ORIG = 210.0   # diámetro rueda trasera original (ficha: 21 cm)
RUEDA_DELANTERA_ORIG = 180.0 # diámetro rueda delantera original (ficha: 18 cm)

# holgura entre la pieza y el tubo; se rellena con una tira de cámara de
# bicicleta (1 mm) que da agarre y protege la pintura del coche
HOLGURA_GOMA = 1.0

# ---------------------------------------------------------------------------
# KIT RUNNING (3 ruedas)
# ---------------------------------------------------------------------------
RUEDA_RUNNING_DIAM = 305.0   # rueda 12" (12 1/2 x 2 1/4) — traseras y delantera
RUEDA_RUNNING_BUJE = 12.0    # eje trasero pasante: barra M12 (ajustar al rodamiento)
EJE_DELANTERO = 10.0         # eje rueda delantera (M10 / 3/8")
BUJE_DELANTERO_ANCHO = 80.0  # largo del buje delantero entre tuercas (O.L.D.) [MEDIR rueda]
SEPARADOR_TRASERO = 55.0     # distancia soporte->rueda para no chocar la rueda original
                             # (si sacas las ruedas originales usa 10)

TUBO_CUADRADO = 20.0         # travesaño delantero: tubo aluminio/acero 20x20
PLETINA_ANCHO = 30.0         # horquilla: pletina de acero 30x5
PLETINA_ESPESOR = 5.0
TRAVESANO_ALTURA = 200.0     # altura del travesaño delantero sobre el suelo, ya convertido
RUEDA_DELANTERA_ADELANTE = 230.0  # cuánto adelanta el eje delantero respecto al travesaño

# ---------------------------------------------------------------------------
# PATINETA (buggy board) + ASIENTO + HAMACA
# ---------------------------------------------------------------------------
TABLA_ANCHO = 400.0   # lateral
TABLA_FONDO = 300.0   # sentido de marcha
TABLA_ALTO = 22.0     # espesor de la tabla impresa (con nervios)
RUEDITA_DIAM = 80.0   # ruedas de patín en línea 80 mm, rodamiento 608
RUEDITA_ANCHO = 24.0
BRAZO_TUBO = 20.0     # brazos: tubo redondo aluminio 20 mm
POSTE_ASIENTO = 25.0  # poste asiento: tubo redondo aluminio 25 mm
CINTA = 25.0          # cinta (webbing) de la hamaca 25 mm

# ---------------------------------------------------------------------------
# BANDEJA
# ---------------------------------------------------------------------------
TABLET_ANCHO = 260.0  # cabe iPad 10.9"/11" con funda
TABLET_FONDO = 185.0
VASO_DIAM = 82.0      # agujero del portavasos (calzos lo reducen a 72 / 62)
