# ---------------------------------------------------------------------
# PARTE 1: FUNCIONES MATEMATICAS
# ---------------------------------------------------------------------

def sumar_filas(matriz):
    """Suma cada fila de una matriz productos x dias."""
    return [sum(fila) for fila in matriz]


def calcular_existencias_finales(iniciales, ventas, reposiciones):
    """Calcula Mf = Mi - Mv + Mr termino a termino."""
    if not (len(iniciales) == len(ventas) == len(reposiciones)):
        raise ValueError("Los tres vectores deben tener la misma dimension.")
    return [
        inicial - venta + reposicion
        for inicial, venta, reposicion in zip(iniciales, ventas, reposiciones)
    ]


def consumo_promedio(ventas_acumuladas, dias):
    """Calcula c = ventas acumuladas / numero de dias."""
    if dias <= 0:
        raise ValueError("El numero de dias debe ser mayor que cero.")
    return ventas_acumuladas / dias


def inventario_en_el_tiempo(inventario_inicial, consumo, tiempo):
    """Funcion afin decreciente I(t) = I0 - c*t."""
    return inventario_inicial - consumo * tiempo


def dias_hasta_minimo(inventario, consumo, stock_minimo):
    """Calcula t = (inventario - stock_minimo) / c."""
    if consumo <= 0:
        return None
    return (inventario - stock_minimo) / consumo


def dias_hasta_agotarse(inventario, consumo):
    """Calcula t = inventario / c."""
    if consumo <= 0:
        return None
    return inventario / consumo


def clasificar_estado(inventario, stock_minimo, dias_minimo):
    if inventario <= stock_minimo:
        return "ALERTA CRITICA"
    if dias_minimo is not None and dias_minimo <= 2:
        return "ALERTA PREVENTIVA"
    return "Normal"


def analizar_periodo(iniciales, stocks_minimos, stocks_optimos,
                     ventas, reposiciones, dias):
    """Calcula todos los resultados del periodo, un diccionario por producto."""
    vendidas = sumar_filas(ventas)
    recibidas = sumar_filas(reposiciones)
    finales = calcular_existencias_finales(iniciales, vendidas, recibidas)

    resultados = []
    for i in range(len(iniciales)):
        consumo = consumo_promedio(vendidas[i], dias)
        d_minimo = dias_hasta_minimo(finales[i], consumo, stocks_minimos[i])
        resultados.append({
            "inicial": iniciales[i],
            "vendidas": vendidas[i],
            "recibidas": recibidas[i],
            "final": finales[i],
            "consumo": consumo,
            "dias_minimo": d_minimo,
            "dias_agotamiento": dias_hasta_agotarse(finales[i], consumo),
            "estado": clasificar_estado(finales[i], stocks_minimos[i], d_minimo),
            "comprar": max(stocks_optimos[i] - finales[i], 0),
        })
    return resultados


# ---------------------------------------------------------------------
# PARTE 2: ENTRADA POR CONSOLA
# ---------------------------------------------------------------------

def pedir_entero(mensaje, minimo=0):
    while True:
        try:
            valor = int(input(mensaje).strip())
            if valor < minimo:
                print(f"Debe ingresar un entero mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Ingrese solo numeros enteros.")


def pedir_texto(mensaje):
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("Este dato no puede quedar vacio.")


def ingresar_productos():
    print("\n=== REGISTRO DE PRODUCTOS ===")
    cantidad = pedir_entero("Cuantos productos desea registrar? ", 1)
    codigos, nombres, iniciales = [], [], []
    stocks_minimos, stocks_optimos = [], []

    for indice in range(cantidad):
        print(f"\n--- Producto {indice + 1} de {cantidad} ---")
        codigos.append(pedir_texto("Codigo (ej: P01): ").upper())
        nombres.append(pedir_texto("Nombre (ej: Arroz 1kg): "))
        iniciales.append(pedir_entero("Cantidad inicial en bodega: "))
        minimo = pedir_entero("Stock minimo de seguridad: ")
        stocks_minimos.append(minimo)
        stocks_optimos.append(
            pedir_entero(
                "Stock optimo (debe ser mayor que el minimo): ",
                minimo=minimo + 1,
            )
        )

    return codigos, nombres, iniciales, stocks_minimos, stocks_optimos


def ingresar_movimientos(nombres, dias):
    ventas = [[0] * dias for _ in nombres]
    reposiciones = [[0] * dias for _ in nombres]

    print("\n=== REGISTRO DIARIO ===")
    for dia in range(dias):
        print(f"\n--- Dia {dia + 1} de {dias} ---")
        for indice, nombre in enumerate(nombres):
            ventas[indice][dia] = pedir_entero(f"{nombre} - unidades vendidas: ")
            reposiciones[indice][dia] = pedir_entero(
                f"{nombre} - unidades recibidas: "
            )
    return ventas, reposiciones


# ---------------------------------------------------------------------
# PARTE 3: PRESENTACION CONSOLA
# ---------------------------------------------------------------------

def mostrar_matriz(titulo, matriz, nombres, dias):
    print(f"\n{titulo}")
    encabezado = f"{'Producto':<16}" + "".join(
        f"{'Dia ' + str(dia + 1):>8}" for dia in range(dias)
    )
    print(encabezado)
    for indice, nombre in enumerate(nombres):
        print(
            f"{nombre:<16}"
            + "".join(f"{valor:>8}" for valor in matriz[indice])
        )


def mostrar_resultados(
    codigos,
    nombres,
    iniciales,
    ventas_acumuladas,
    reposiciones_acumuladas,
    existencias_finales,
    estados,
):
    print("\n=== TABLA RESUMEN DEL PERIODO ===")
    print(
        f"{'Codigo':<8}{'Producto':<16}{'Inicial':>8}{'Ventas':>8}"
        f"{'Repos.':>8}{'Final':>8}  Estado"
    )
    for indice, codigo in enumerate(codigos):
        print(
            f"{codigo:<8}{nombres[indice]:<16}{iniciales[indice]:>8}"
            f"{ventas_acumuladas[indice]:>8}{reposiciones_acumuladas[indice]:>8}"
            f"{existencias_finales[indice]:>8}  {estados[indice]}"
        )


def procesar_periodo(codigos, nombres, iniciales, stocks_minimos,
                     stocks_optimos, ventas, reposiciones, dias):
    mostrar_matriz("Matriz de VENTAS", ventas, nombres, dias)
    mostrar_matriz("Matriz de REPOSICIONES", reposiciones, nombres, dias)

    res = analizar_periodo(iniciales, stocks_minimos, stocks_optimos,
                           ventas, reposiciones, dias)
    vendidas = [r["vendidas"] for r in res]
    recibidas = [r["recibidas"] for r in res]
    existencias = [r["final"] for r in res]
    estados = [r["estado"] for r in res]

    mostrar_resultados(codigos, nombres, iniciales, vendidas,
                       recibidas, existencias, estados)
    print(f"\nTotal vendido: {sum(vendidas)} unidades")
    print(f"Existencias finales: {sum(existencias)} unidades")

    mayor = max(vendidas) if vendidas else 0
    if mayor > 0:
        indice = vendidas.index(mayor)
        print(f"Producto mas vendido: {nombres[indice]} ({mayor} unidades)")

    for indice, nombre in enumerate(nombres):
        r = res[indice]
        if r["estado"] == "Normal":
            continue
        print(f"\n[{r['estado']} DE REPOSICION]")
        print(f"Producto: {codigos[indice]} - {nombre}")
        print(
            f"Stock actual: {r['final']} "
            f"(nivel minimo: {stocks_minimos[indice]}), "
            f"comprar {r['comprar']} unidades."
        )
        if r["dias_minimo"] is not None:
            print(f"Dias hasta el minimo: {r['dias_minimo']:.2f}")
        if r["dias_agotamiento"] is not None:
            print(f"Dias hasta agotamiento: {r['dias_agotamiento']:.2f}")

    print("\n=== PROYECCION I(t) = Mf - c*t (7 dias) ===")
    for indice, nombre in enumerate(nombres):
        valores = [
            max(inventario_en_el_tiempo(existencias[indice],
                                        res[indice]["consumo"], dia), 0)
            for dia in range(8)
        ]
        print(f"{nombre:<16}: {valores}")

    return existencias


# ---------------------------------------------------------------------
# PARTE 4: DATOS DEMO Y PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------

def datos_demo():
    codigos = ["P01", "P02", "P03"]
    nombres = ["Arroz 1kg", "Aceite 1L", "Azucar 1kg"]
    iniciales = [50, 30, 20]
    stocks_minimos = [20, 25, 15]
    stocks_optimos = [60, 40, 30]
    ventas = [
        [3, 2, 3, 2, 2],
        [2, 1, 2, 2, 1],
        [1, 2, 0, 1, 1],
    ]
    reposiciones = [
        [0, 0, 10, 0, 0],
        [0, 5, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    return codigos, nombres, iniciales, stocks_minimos, stocks_optimos, ventas, reposiciones, 5


def main():
    print("=" * 60)
    print("PRISMASTOCK - Control y proyeccion de inventario")
    print("=" * 60)
    print("1) Ejecutar demostracion")
    print("2) Ingresar mis propios productos")
    opcion = pedir_entero("Elija una opcion: ", 1)
    while opcion not in (1, 2):
        opcion = pedir_entero("Opcion invalida. Elija 1 o 2: ", 1)

    if opcion == 1:
        datos = datos_demo()
        codigos, nombres, iniciales, stocks_minimos, stocks_optimos, ventas, reposiciones, dias = datos
    else:
        codigos, nombres, iniciales, stocks_minimos, stocks_optimos = ingresar_productos()
        dias = pedir_entero("Cuantos dias tiene el periodo? ", 1)
        ventas, reposiciones = ingresar_movimientos(nombres, dias)

    periodo = 1
    while True:
        print(f"\n{'=' * 60}\nRESULTADOS DEL PERIODO {periodo}\n{'=' * 60}")
        iniciales = procesar_periodo(
            codigos,
            nombres,
            iniciales,
            stocks_minimos,
            stocks_optimos,
            ventas,
            reposiciones,
            dias,
        )
        repetir = input(
            "\nRegistrar otro periodo con este stock como inicial? (s/n): "
        ).strip().lower()
        if repetir != "s":
            break
        periodo += 1
        dias = pedir_entero("Dias del nuevo periodo: ", 1)
        ventas, reposiciones = ingresar_movimientos(nombres, dias)

    print("\nGracias por usar PrismaStock.")


if __name__ == "__main__":
    main()
