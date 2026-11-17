import unittest

from prismastock import (
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
        self.assertEqual(inventario_en_el_tiempo(27, 1.6, 1), 25.4)
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


if __name__ == "__main__":
    unittest.main()
