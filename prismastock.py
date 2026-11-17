# ---------------------------------------------------------------------
# PARTE 1: FUNCIONES MATEMÁTICAS (el "motor" del programa)
# ---------------------------------------------------------------------

def sumar_filas(matriz):
    """
    SUMATORIA por filas.
    Para cada fila i calcula:  total[i] = suma de matriz[i][j]  (j = 1..n)
    Ejemplo: [[3,2,3,2,2],[2,1,2,2,1]]  ->  [12, 8]
    Devuelve un vector columna (n x 1) representado como lista.
    """
    totales = []
    for fila in matriz:
        suma = 0
        for valor in fila:
            suma = suma + valor
        totales.append(suma)
    return totales


def calcular_existencias_finales(Mi, Mv, Mr):
    """
    OPERACIÓN MATRICIAL:  Mf = Mi - Mv + Mr
    Se opera término a término (las tres matrices son n x 1,
    es decir, tienen la misma dimensión).
    """
    Mf = []
    for i in range(len(Mi)):
        Mf.append(Mi[i] - Mv[i] + Mr[i])
    return Mf


def consumo_promedio(ventas_acumuladas, dias):
    """
    PROMEDIO:  c = ventas acumuladas / número de días
    Es la pendiente (con signo negativo) de la función afín.
    """
    return ventas_acumuladas / dias


def inventario_en_el_tiempo(Mf, c, t):
    """
    FUNCIÓN AFÍN DECRECIENTE:  I(t) = Mf - c*t
      Mf = inventario de partida (I0 del nuevo período)
      c  = consumo diario constante (unidades/día)
      t  = días transcurridos
    """
    return Mf - c * t


def dias_hasta_minimo(Mf, c, stock_min):
    """
    DESPEJE de t en  I(t) = Imin :
        Mf - c*t = Imin   ->   t = (Mf - Imin) / c
    Si c = 0 (no se vende nada) el stock nunca baja: devuelve None.
    """
    if c <= 0:
        return None
    return (Mf - stock_min) / c


def dias_hasta_agotarse(Mf, c):
    """
    DESPEJE de t en  I(t) = 0 :   t = Mf / c
    """
    if c <= 0:
        return None
    return Mf / c


def clasificar_estado(Mf, stock_min, t_min):
    """
    REGLAS DE ALERTA (las mismas de la Etapa 2):
      - Mf <= stock_min           -> ALERTA CRÍTICA
      - si no, y t <= 2 días      -> ALERTA PREVENTIVA
      - en cualquier otro caso    -> NORMAL
    """
    if Mf <= stock_min:
        return "ALERTA CRÍTICA"
    if t_min is not None and t_min <= 2:
        return "ALERTA PREVENTIVA"
    return "Normal"


# ---------------------------------------------------------------------
# PARTE 2: ENTRADA DE DATOS (con validación para que no se caiga)
# ---------------------------------------------------------------------

def pedir_entero(mensaje, minimo=0):
    """Pide un número entero >= minimo y repite hasta que sea válido."""
    while True:
        texto = input(mensaje).strip()
        try:
            valor = int(texto)
            if valor < minimo:
                print(f"   ⚠ Debe ser un número entero mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("   ⚠ Ingrese solo números enteros (sin letras ni decimales).")


def pedir_texto(mensaje):
    """Pide un texto que no esté vacío."""
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("   ⚠ Este dato no puede quedar vacío.")


def ingresar_productos():
    """
    PASO 1 (ficha): ingreso de productos.
    Guarda en LISTAS PARALELAS: la posición i identifica al mismo producto
    en todas las listas.
    """
    print("\n=== PASO 1: REGISTRO DE PRODUCTOS ===")
    n = pedir_entero("¿Cuántos productos desea registrar? ", minimo=1)

    codigos, nombres = [], []
    Mi, stock_min, stock_opt = [], [], []

    for i in range(n):
        print(f"\n--- Producto {i + 1} de {n} ---")
        codigos.append(pedir_texto("Código (ej: P01): ").upper())
        nombres.append(pedir_texto("Nombre (ej: Arroz 1kg): "))
        Mi.append(pedir_entero("Cantidad inicial en bodega (I0): "))
        minimo = pedir_entero("Stock mínimo de seguridad (Imín): ")
        stock_min.append(minimo)
        # El stock óptimo debe ser mayor que el mínimo, si no no tiene sentido
        optimo = pedir_entero("Stock óptimo (cantidad a la que desea volver al reponer): ",
                              minimo=minimo + 1)
        stock_opt.append(optimo)

    return codigos, nombres, Mi, stock_min, stock_opt


def ingresar_movimientos(nombres, dias):
    """
    PASO 3 (ficha): registro diario de ventas y reposiciones.
    Construye dos MATRICES de dimensión (productos x días):
        V[i][j] = unidades vendidas del producto i el día j
        R[i][j] = unidades recibidas del producto i el día j
    """
    n = len(nombres)
    V = [[0] * dias for _ in range(n)]   # matriz de ceros n x dias
    R = [[0] * dias for _ in range(n)]

    print("\n=== PASO 3: REGISTRO DIARIO DE VENTAS Y REPOSICIONES ===")
    for j in range(dias):
        print(f"\n--- Día {j + 1} de {dias} ---")
        for i in range(n):
            V[i][j] = pedir_entero(f"  {nombres[i]} - unidades vendidas: ")
            R[i][j] = pedir_entero(f"  {nombres[i]} - unidades recibidas (reposición): ")
    return V, R


# ---------------------------------------------------------------------
# PARTE 3: SALIDA POR PANTALLA
# ---------------------------------------------------------------------

def mostrar_matriz(titulo, matriz, nombres, dias):
    """Dibuja una matriz productos x días con encabezados."""
    print(f"\n{titulo}")
    encabezado = f"{'Producto':<16}" + "".join(f"{'Día ' + str(j + 1):>7}" for j in range(dias))
    print(encabezado)
    print("-" * len(encabezado))
    for i in range(len(matriz)):
        fila = f"{nombres[i]:<16}" + "".join(f"{v:>7}" for v in matriz[i])
        print(fila)


def mostrar_tabla_resumen(codigos, nombres, Mi, Mv, Mr, Mf, estados):
    """PASO 6 (ficha): tabla resumen formateada."""
    print("\n=== TABLA RESUMEN DEL PERÍODO ===")
    cab = (f"{'Cód':<5}{'Producto':<16}{'Inicial':>8}{'Ventas':>8}"
           f"{'Repos.':>8}{'Final':>7}  {'Estado'}")
    print(cab)
    print("-" * (len(cab) + 10))
    for i in range(len(codigos)):
        print(f"{codigos[i]:<5}{nombres[i]:<16}{Mi[i]:>8}{Mv[i]:>8}"
              f"{Mr[i]:>8}{Mf[i]:>7}  {estados[i]}")


def mostrar_totales(Mv, Mf):
    """Sumatorias globales de los vectores columna (como en la ficha)."""
    total_vendido = sum(Mv)   # sumatoria de i=1..n de Mv[i]
    total_existencias = sum(Mf)
    print(f"\nTotal de unidades vendidas en el período : {total_vendido}")
    print(f"Total de existencias finales en bodega   : {total_existencias}")


def mostrar_mas_vendido(nombres, Mv):
    """Identifica el producto más vendido comparando ventas acumuladas."""
    mayor = max(Mv)
    if mayor == 0:
        print("\nNo se registraron ventas en el período.")
        return
    i = Mv.index(mayor)
    print(f"Producto más vendido: {nombres[i]} ({mayor} unidades)")


def mostrar_alertas(codigos, nombres, Mf, c, stock_min, stock_opt, estados, t_min):
    """Alertas con recomendación de compra (stock_opt - Mf)."""
    hay_alertas = False
    for i in range(len(codigos)):
        if estados[i] == "Normal":
            continue
        hay_alertas = True
        t_cero = dias_hasta_agotarse(Mf[i], c[i])
        a_comprar = max(stock_opt[i] - Mf[i], 0)

        if estados[i] == "ALERTA CRÍTICA":
            print("\n[ALERTA CRÍTICA DE REPOSICIÓN]")
        else:
            print("\n[ALERTA PREVENTIVA DE REPOSICIÓN]")
        print(f"  Producto: {codigos[i]} - {nombres[i]}")
        print(f"  Stock actual: {Mf[i]} unidades (nivel mínimo: {stock_min[i]})")
        print(f"  Consumo promedio: {c[i]:.2f} unidades/día")
        if estados[i] == "ALERTA PREVENTIVA":
            print(f"  Alcanzará su nivel mínimo en: {t_min[i]:.2f} días")
        if t_cero is not None:
            print(f"  Tiempo estimado para desabastecimiento total: {t_cero:.2f} días")
        print(f"  Recomendación: comprar {a_comprar} unidades para volver al "
              f"stock óptimo de {stock_opt[i]}.")

    if not hay_alertas:
        print("\nNingún producto requiere reposición por ahora. ✔")


def mostrar_proyeccion(nombres, Mf, c, horizonte=7):
    """Tabla de la función afín I(t) = Mf - c*t para los próximos días."""
    print(f"\n=== PROYECCIÓN I(t) = Mf - c·t  (próximos {horizonte} días) ===")
    cab = f"{'Producto':<16}" + "".join(f"{'t=' + str(t):>7}" for t in range(horizonte + 1))
    print(cab)
    print("-" * len(cab))
    for i in range(len(nombres)):
        fila = f"{nombres[i]:<16}"
        for t in range(horizonte + 1):
            valor = max(inventario_en_el_tiempo(Mf[i], c[i], t), 0)  # no hay stock negativo
            fila += f"{valor:>7.1f}"
        print(fila)


# ---------------------------------------------------------------------
# PARTE 4: PROCESAMIENTO COMPLETO DE UN PERÍODO
# ---------------------------------------------------------------------

def procesar_periodo(codigos, nombres, Mi, stock_min, stock_opt, V, R, dias):
    """
    Ejecuta los pasos 4, 5 y 6 de la ficha y devuelve Mf
    (que será el inventario inicial del siguiente período).
    """
    mostrar_matriz("Matriz de VENTAS (V)", V, nombres, dias)
    mostrar_matriz("Matriz de REPOSICIONES (R)", R, nombres, dias)

    # Sumatorias por fila -> vectores acumulados
    Mv = sumar_filas(V)
    Mr = sumar_filas(R)

    # PASO 4: Mf = Mi - Mv + Mr
    Mf = calcular_existencias_finales(Mi, Mv, Mr)

    # PASO 5: consumo promedio, días hasta el mínimo y estado
    c, t_min, estados = [], [], []
    for i in range(len(codigos)):
        ci = consumo_promedio(Mv[i], dias)
        ti = dias_hasta_minimo(Mf[i], ci, stock_min[i])
        c.append(ci)
        t_min.append(ti)
        estados.append(clasificar_estado(Mf[i], stock_min[i], ti))

    # PASO 6: resultados
    mostrar_tabla_resumen(codigos, nombres, Mi, Mv, Mr, Mf, estados)
    mostrar_totales(Mv, Mf)
    mostrar_mas_vendido(nombres, Mv)

    print("\n=== CONSUMO PROMEDIO Y DÍAS HASTA EL MÍNIMO ===")
    for i in range(len(codigos)):
        if t_min[i] is None:
            texto_t = "sin consumo (no se proyecta agotamiento)"
        else:
            texto_t = f"{max(t_min[i], 0):.2f} días hasta el mínimo"
        print(f"  {nombres[i]:<16} c = {Mv[i]}/{dias} = {c[i]:.2f} unid./día  ->  {texto_t}")

    mostrar_alertas(codigos, nombres, Mf, c, stock_min, stock_opt, estados, t_min)
    mostrar_proyeccion(nombres, Mf, c)
    return Mf


# ---------------------------------------------------------------------
# PARTE 5: DATOS DE DEMOSTRACIÓN (el minimarket de la Etapa 2)
# ---------------------------------------------------------------------

def datos_demo():
    """Reproduce exactamente el ejemplo de la ficha de la Etapa 2."""
    codigos = ["P01", "P02", "P03"]
    nombres = ["Arroz 1kg", "Aceite 1L", "Azúcar 1kg"]
    Mi = [50, 30, 20]
    stock_min = [20, 25, 15]
    stock_opt = [60, 40, 30]
    V = [[3, 2, 3, 2, 2],     # Arroz  -> suma 12
         [2, 1, 2, 2, 1],     # Aceite -> suma 8
         [1, 2, 0, 1, 1]]     # Azúcar -> suma 5
    R = [[0, 0, 10, 0, 0],    # Arroz  -> suma 10
         [0, 5, 0, 0, 0],     # Aceite -> suma 5
         [0, 0, 0, 0, 0]]     # Azúcar -> suma 0
    return codigos, nombres, Mi, stock_min, stock_opt, V, R, 5


# ---------------------------------------------------------------------
# PARTE 6: PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------

def main():
    print("=" * 60)
    print("   PRISMASTOCK - Control y proyección de inventario")
    print("=" * 60)
    print("1) Ejecutar demostración (minimarket de ejemplo)")
    print("2) Ingresar mis propios productos")
    opcion = pedir_entero("Elija una opción (1 o 2): ", minimo=1)
    while opcion not in (1, 2):
        opcion = pedir_entero("Opción inválida. Elija 1 o 2: ", minimo=1)

    if opcion == 1:
        codigos, nombres, Mi, stock_min, stock_opt, V, R, dias = datos_demo()
        print("\n(Se usan los datos de la ficha: 3 productos, 5 días.)")
    else:
        codigos, nombres, Mi, stock_min, stock_opt = ingresar_productos()
        dias = pedir_entero("\n¿Cuántos días tiene el período a registrar? ", minimo=1)
        V, R = ingresar_movimientos(nombres, dias)

    periodo = 1
    while True:
        print(f"\n{'=' * 60}\n   RESULTADOS DEL PERÍODO {periodo}\n{'=' * 60}")
        Mf = procesar_periodo(codigos, nombres, Mi, stock_min, stock_opt, V, R, dias)

        otra = input("\n¿Desea registrar otro período usando estas existencias "
                     "finales como inventario inicial? (s/n): ").strip().lower()
        if otra != "s":
            break
        # El Mf de este período pasa a ser el Mi del siguiente
        Mi = Mf
        periodo += 1
        dias = pedir_entero("¿Cuántos días tiene este nuevo período? ", minimo=1)
        V, R = ingresar_movimientos(nombres, dias)

    print("\nGracias por usar PrismaStock. ¡Hasta pronto!")


if __name__ == "__main__":
    main()
