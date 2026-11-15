# Guía de montaje

Herramientas: llaves 8/10/13/17/19 mm, llave Allen, taladro con brocas de 6,5 y 10,5 mm, sierra para metal, lima, pie de metro y tijeras.

En todas las abrazaderas de tubo:
1. Envuelve el tubo con **una vuelta de cámara de bicicleta** (tira del ancho de la pieza).
2. Pon las **tuercas en sus alojamientos hexagonales**.
3. Aprieta los pernos **en cruz** y de forma pareja, hasta que la pieza no gire con la mano. No sigas apretando: el plástico se puede partir.

---

## A. Kit running (3 ruedas)

### A1. Eje trasero
1. Corta la **barra roscada M12** al largo de `docs/cortes_metal.md` y lima las puntas.
2. Instala en cada pata trasera un **soporte_eje_trasero** (A + B_tapa):
   - la parte A, con el buje del eje, va **hacia atrás**;
   - bájalo hasta que su cara inferior **descanse sobre la carcasa de la rueda original** (ese es el tope);
   - aprieta 4 pernos M6x50.
3. Pasa la barra por ambos soportes. Arma cada lado de adentro hacia afuera:
   **tuerca M12 + golilla, contra el soporte → separador_eje → golilla → rueda → golilla → tuerca autoblocante M12**.
   Ajusta hasta que la rueda gire libre y sin juego lateral.
   - El `collarin_eje` es un respaldo opcional entre separador y soporte.
4. Comprueba que las ruedas originales queden en el aire (~5 cm) y que las nuevas no rocen con nada. Si alguna roza, cambia `SEPARADOR_TRASERO` y vuelve a imprimir los separadores.

### A2. Travesaño y horquilla delantera
1. Corta el **tubo 20x20**, ponle los 2 `tapon_tubo_cuadrado` y pásalo por los 2 `soporte_travesano_delantero` (A + tapa).
2. Monta los soportes en las patas delanteras:
   - el canal del tubo va **hacia adelante**;
   - apoya los soportes sobre la carcasa de las ruedas delanteras y ajusta su altura para que el travesaño quede a `TRAVESANO_ALTURA` (200 mm) del suelo, ya con las ruedas traseras nuevas puestas;
   - aprieta.
3. Perfora el tubo en vertical a través del agujero de cada soporte (broca 6,5) y pon un **M6x40**. Así el travesaño no puede girar.
4. Imprime la plantilla `plantilla_pletina_horquilla_1a1.svg` **al 100 %** y comprueba la regla de 100 mm. Pégala sobre la pletina, marca con punto y perfora (6,5 / 6,5 / 10,5). En **una** de las pletinas haz el agujero del eje como **ranura** de 16 mm (dos agujeros juntos y lima).
5. Pon el `separador_horquilla` en el centro del travesaño, con la punta hacia adelante y abajo. Perfora el tubo a través de su agujero vertical y fija con un M6x40.
6. Arma **pletina – separador – pletina** con 2 pernos **M6x100** y tuercas autoblocantes. Monta la rueda delantera entre las pletinas con su eje M10 (o 3/8").
7. **Alineación:**
   - empuja el coche suelto por una superficie plana, unos 10 m;
   - si se desvía, suelta la tuerca del lado de la ranura, mueve el eje 1–2 mm y repite.
8. Ata la **correa de muñeca** al manillar.

**Volver al modo paseo:** quita las 2 tuercas M12 y las ruedas traseras, y saca la horquilla con los 2 M6x100. Si quieres, deja puestos los soportes, que no molestan.

---

## B. Patineta + sillín

### B1. Tabla
1. Une las 4 baldosas con **12 pernos M5x20** a través de las paredes de unión.
2. Atornilla por arriba (todos con M6 y tuercas abajo):
   - la `placa_pivote` adelante al centro (4 x M6x40);
   - la `placa_central_asiento` al centro, que une las 4 baldosas (4 x M6x35);
   - las 2 `horquilla_ruedita` por debajo, atrás (4 x M6x35).
3. Pega la lija antideslizante, dejando libres la placa central y la placa pivote.
4. Monta las ruedas de 80 mm: **2 rodamientos 608 + golillas a cada lado**, eje **M8x60** y tuerca autoblocante.

### B2. Pivote y brazos
1. Pon el **perno M10x60** desde arriba en el `bloque_giratorio`, pasando por la placa pivote y la tabla. Tuerca autoblocante abajo, con el ajuste justo para que gire suave.
2. Corta los 2 tubos Ø20. Arma:
   - un extremo de cada tubo en el `yugo_brazos`;
   - el otro extremo en un `terminal_brazo`;
   - perfora cada unión a través del agujero de la pieza (broca 5) y fija con M5x35.
3. Pon la lengüeta del yugo entre las orejas del bloque giratorio y fíjala con un **M8x50** y golillas de nylon.
4. Instala en cada pata trasera, **encima** del soporte del eje, una `abrazadera_pivote_pata` (A + tapa), con la oreja **hacia atrás**.
5. Une cada `terminal_brazo` a la **cara interior** de la oreja con un M8x50, golilla de nylon entre ambas piezas y tuerca autoblocante. Debe pivotar libre.
6. Para guardarla, levanta la patineta y amárrala al manillar con una cinta con velcro.

### B3. Sillín
1. Corta el poste Ø25 (300 mm) y perfóralo cada 25 mm, en cruz, con broca 6,5.
2. Mete el poste en el zócalo de la placa central y en el `asiento_sillin`. Fija la altura con 2 pernos M6x45 o pasadores tipo "R".
3. Altura recomendada: con la niña sentada, sus pies deben tocar la tabla y sus manos llegar cómodas al manillar.

---

## C. Hamaca (modo siesta)

### C1. Anclajes impresos
- Monta 2 `anclaje_manillar` (A + tapa, M5x35) en los tubos laterales del manillar, a la altura donde quieras que quede la cabeza.
- Los anclajes inferiores ya vienen incluidos: son las ranuras de las `abrazadera_pivote_pata`.

### C2. Costura (lona Cordura 600D)
```
        ┌──────── 38 cm ────────┐
        │  bolsillo espuma 10mm │  ← respaldo + cabecera (alas laterales
        │      (35 x 55 cm)     │     de 8 cm a cada lado, a la altura
        │                       │     de la cabeza)
   70cm │                       │
        │                       │
        ├───────────────────────┤  ← costura reforzada: cinturón (hebilla de
        │   asiento (38 x 30)   │     seguridad de 25 mm) a cada lado
        │  4 ojales → sillín    │
        ├───────────────────────┤
   20cm │    faldón delantero   │  ← 2 cintas a anclajes inferiores
        └───────────────────────┘
```
- **Arriba:** 2 cintas de 25 mm cosidas en "caja con X" (cuadrado con una X cosida adentro). Pasan por la ranura del anclaje y vuelven a una **hebilla escalera** para regular el largo.
- **Abajo:** 2 cintas desde el faldón a las ranuras de las abrazaderas de pata, también con hebilla escalera.
- **Asiento:** 4 cintas cortas que se amarran por los 4 ojales del sillín. El fondo de la hamaca debe quedar **apoyado y amarrado al sillín**, no colgando.
- Agrega una cinta de entrepierna, que va del faldón al cinturón, para que la niña no se deslice hacia abajo al dormirse.

### C3. Uso
1. Ajusta las cintas superiores hasta que el respaldo quede reclinado unos 30°.
2. Sienta a la niña en el sillín, mirando hacia el coche, con la espalda en la lona. Abrocha el cinturón.
3. Camina a paso normal. **No trotes con la hamaca puesta.**

---

## D. Bandeja
1. Une las 2 mitades por los nervios centrales con **3 pernos M4x20**.
2. Monta las 2 abrazaderas de manillar, cada una con su parte superior + inferior y 2 pernos M5x25:
   - separadas **180 mm** entre centros, simétricas;
   - con la pestaña **hacia adelante** y horizontal.
3. Atornilla la bandeja a las pestañas con 4 pernos M5x20. Las tuercas van cautivas en la pestaña.
4. Atornilla un portavasos bajo cada borde lateral con 2 pernos M4x12. Las tuercas van cautivas en el portavasos.
5. Pon los calzos de TPU si tus vasos son más angostos (72 o 62 mm).
6. Los `vaso_350ml` impresos sirven para snacks secos. Para líquidos o comida húmeda, mejor usa vasos comerciales: el plástico impreso tiene microporos difíciles de lavar.
