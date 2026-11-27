import unittest

from prismastock import (
    analizar_periodo,
    calcular_existencias_finales,
    clasificar_estado,
    consumo_promedio,
    datos_demo,
    dias_hasta_minimo,
    inventario_en_el_tiempo,
    sumar_filas,
)


class PrismaStockTests(unittest.TestCase):
    def test_demo_week_calculations(self):
        codigos, nombres, iniciales, _, _, ventas, reposiciones, dias = datos_demo()
        sold = sumar_filas(ventas)
        received = sumar_filas(reposiciones)
        final = calcular_existencias_finales(iniciales, sold, received)

        self.assertEqual(sold, [12, 8, 5])
        self.assertEqual(received, [10, 5, 0])
        self.assertEqual(final, [48, 27, 15])
        self.assertEqual(sum(sold), 25)
        self.assertEqual(len(codigos), len(nombres))
        self.assertEqual(dias, 5)

    def test_affine_projection_and_alerts(self):
        average = consumo_promedio(8, 5)
        days = dias_hasta_minimo(27, average, 25)

        self.assertAlmostEqual(average, 1.6)
        self.assertAlmostEqual(days, 1.25)
        self.assertAlmostEqual(inventario_en_el_tiempo(27, 1.6, 1), 25.4)
        self.assertEqual(
            clasificar_estado(27, 25, days),
            "ALERTA PREVENTIVA",
        )
        self.assertEqual(
            clasificar_estado(15, 15, 0),
            "ALERTA CRITICA",
        )

    def test_reject_mismatched_vectors(self):
        with self.assertRaises(ValueError):
            calcular_existencias_finales([50, 30], [12], [10, 5])

    def test_no_sales_has_no_projection_or_alert(self):
        self.assertIsNone(dias_hasta_minimo(30, 0, 20))

    def test_analyze_period(self):
        _, _, iniciales, minimos, optimos, ventas, reposiciones, dias = datos_demo()

        resultados = analizar_periodo(
            iniciales, minimos, optimos, ventas, reposiciones, dias
        )

        self.assertEqual(len(resultados), 3)
        self.assertEqual(resultados[0]["inicial"], 50)
        self.assertEqual(resultados[0]["vendidas"], 12)
        self.assertEqual(resultados[0]["recibidas"], 10)
        self.assertEqual(resultados[0]["final"], 48)
        self.assertAlmostEqual(resultados[0]["consumo"], 2.4)
        self.assertAlmostEqual(resultados[0]["dias_minimo"], 28 / 2.4)
        self.assertEqual(resultados[0]["dias_agotamiento"], 20.0)
        self.assertEqual(resultados[0]["estado"], "Normal")
        self.assertEqual(resultados[0]["comprar"], 12)
        self.assertEqual(resultados[1]["estado"], "ALERTA PREVENTIVA")
        self.assertEqual(resultados[1]["comprar"], 13)
        self.assertEqual(resultados[2]["estado"], "ALERTA CRITICA")
        self.assertEqual(resultados[2]["comprar"], 15)


if __name__ == "__main__":
    unittest.main()
