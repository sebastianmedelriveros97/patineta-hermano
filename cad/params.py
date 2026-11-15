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
PATA_DELANTERA_ANGULO = 36.0 # [MEDIR] inclinación del tubo manillar->rueda delantera respecto a la vertical (fotos: ~36°)

MANILLAR_DIAM = 28.0         # [MEDIR] diámetro del manillar CON la espuma
TUBO_LATERAL_MANILLAR_DIAM = 26.0  # [MEDIR] tubos laterales del manillar (anclaje hamaca)

ANCHO_CHASIS = 470.0         # ancho exterior entre patas traseras (ficha: 47 cm)
RUEDA_TRASERA_ORIG = 210.0   # diámetro rueda trasera original (ficha: 21 cm)
RUEDA_DELANTERA_ORIG = 180.0 # diámetro rueda delantera original (ficha: 18 cm)

# holgura entre la pieza y el tubo; se rellena con una tira de cámara de
# bicicleta (1 mm) que da agarre y protege la pintura del coche
HOLGURA_GOMA = 1.0

# Geometría lateral del coche, calibrada con las fotos del Leona 2 (escala por alto 1035 mm).
# Origen = centro de la rueda delantera original, X hacia ATRÁS, Z hacia arriba.
# El chasis es una "X": un tubo recto va del manillar a la rueda delantera; la pata trasera
# baja desde el buje del asiento hasta el conjunto trasero (ruedas juntas con resortes y freno central).
EJE_TRASERO_ORIG_X = 460.0   # [MEDIR] distancia entre ejes original (fotos: ~46 cm)
PATA_TRASERA_ANGULO = 39.0   # [MEDIR] inclinación de la pata trasera respecto a la vertical
PATA_TRASERA_BASE_X = 400.0  # [MEDIR] extremo inferior de la pata trasera (donde empieza el conjunto trasero)
PATA_TRASERA_TOPE_Z = 190.0  # [MEDIR] altura de ese extremo inferior
PATA_DELANTERA_TOPE_Z = 185.0  # [MEDIR] altura de la parte superior del giratorio de la rueda delantera
PATA_SEPARACION = 420.0      # [MEDIR] distancia entre centros de las 2 patas traseras (y delanteras)
RUEDAS_TRASERAS_ORIG_Y = 130.0  # [MEDIR] distancia del centro del coche al centro de cada rueda trasera original
RUEDAS_DELANTERAS_ORIG_Y = 180.0  # [MEDIR] ídem ruedas delanteras
MANILLAR_X = 765.0
MANILLAR_Z = 1015.0
MANILLAR_BOTON_ANCHO = 190.0  # [MEDIR] ancho de la caja del botón de plegado al centro del manillar

# ---------------------------------------------------------------------------
# KIT RUNNING (3 ruedas)
# ---------------------------------------------------------------------------
# Ruedas: 3 x rueda EVA (espuma maciza, SIN cámara) aro 12", tipo repuesto de bicicleta de
# equilibrio. Livianas (~0,5 kg c/u) y no se pinchan. Las 3 ruedas son iguales.
RUEDA_RUNNING_DIAM = 300.0   # [MEDIR rueda] diámetro exterior EVA 12" (≈ 29–30 cm)
RUEDA_RUNNING_ANCHO = 55.0   # [MEDIR rueda] ancho del neumático EVA
EJE_RUEDA = 10.0             # [MEDIR rueda] eje roscado de la rueda (M10 típico; si es M8 pon 8)
BUJE_ANCHO = 80.0            # [MEDIR rueda] ancho del buje entre las caras donde apoyan las tuercas
ELEVACION = 52.0             # cuánto sube el coche en modo trote (las ruedas originales quedan en el aire)
EJE_TRASERO_ATRAS = 40.0     # el eje trasero nuevo va un poco detrás del original (las ruedas originales
                             # van juntas al centro, así que las nuevas pasan por fuera sin chocar)

# Enganche rápido ("enclachar"): pasadores de bola con botón (quick release pin)
PASADOR_D = 6.0              # kit trote: pasador de bola Ø6 x 40 mm (4 unidades)
PASADOR_PATINETA_D = 8.0     # patineta: pasador de bola Ø8 x 50 mm (2 unidades)

TUBO_CUADRADO = 20.0         # travesaños delantero y trasero: tubo cuadrado 20x20x2
PLETINA_ANCHO = 30.0         # horquilla: pletina de acero 30x5
PLETINA_ESPESOR = 5.0
TRAVESANO_ALTURA = 300.0     # altura del travesaño delantero sobre el suelo, ya convertido
                             # (debe quedar SOBRE la horquilla giratoria de la rueda original)
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
