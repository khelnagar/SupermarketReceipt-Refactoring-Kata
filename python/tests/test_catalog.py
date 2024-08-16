import unittest

from catalog import SupermarketCatalog
from model_objects import Product, ProductUnit


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.catalog = SupermarketCatalog()
        self.product = Product("product", ProductUnit.EACH)

    def test_calling_add_product_raised_exception(self):
        with self.assertRaises(Exception) as context:
            self.catalog.add_product(self.product, 1)
        self.assertEqual(
            "cannot be called from a unit test - it accesses the database",
            str(context.exception),
        )

    def test_calling_unit_price_raised_exception(self):
        with self.assertRaises(Exception) as context:
            self.catalog.unit_price(self.product)
        self.assertEqual(
            "cannot be called from a unit test - it accesses the database",
            str(context.exception),
        )
