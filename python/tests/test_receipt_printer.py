import unittest

from approvaltests import verify

from model_objects import Product, SpecialOfferType, ProductUnit, Discount
from receipt import Receipt
from receipt_printer import ReceiptPrinter


class ReceiptPrinterTest(unittest.TestCase):
    def setUp(self):
        self.toothbrush = Product("toothbrush", ProductUnit.EACH)
        self.apples = Product("apples", ProductUnit.KILO)
        self.receipt = Receipt()
        self.printer = ReceiptPrinter()

        self.toothbrush_price = 0.99
        self.apples_price = 1.99

    def test_one_item(self):
        self.receipt.add_product(self.toothbrush, 1, self.toothbrush_price, self.toothbrush_price)
        verify(self.printer.print_receipt(self.receipt))

    def test_two_items_same(self):
        self.receipt.add_product(self.toothbrush, 2, self.toothbrush_price, 2 * self.toothbrush_price)
        verify(self.printer.print_receipt(self.receipt))

    def test_fraction_kilo(self):
        self.receipt.add_product(self.apples, 0.75, self.apples_price, 0.75 * self.apples_price)
        verify(self.printer.print_receipt(self.receipt))

    def test_multiple_items(self):
        self.receipt.add_product(self.toothbrush, 2, self.toothbrush_price, 2 * self.toothbrush_price)
        self.receipt.add_product(self.apples, 0.75, self.apples_price, 0.75 * self.apples_price)
        verify(self.printer.print_receipt(self.receipt))

    def test_discount_three_for_two(self):
        # We're adding the product and discount directly on the receipt and not through the cart/checkout process.
        # This is to test the printer in isolation, otherwise, a change of how cart displays discount for example would
        # break the printer tests but in fact, the printer works properly (does what it has to do)
        self.receipt.add_product(self.apples, 3, self.apples_price, 3 * self.apples_price)
        self.receipt.add_discount(Discount(self.apples, "3 for 2", -1.99))
        verify(self.printer.print_receipt(self.receipt))

    def test_discount_ten_percent(self):
        self.receipt.add_product(self.apples, 1, self.apples_price, self.apples_price)
        self.receipt.add_discount(Discount(self.apples, "10.0% off", -0.20))
        verify(self.printer.print_receipt(self.receipt))

    def test_discount_two_for_amount(self):
        self.receipt.add_product(self.apples, 2, self.apples_price, 3.98)
        self.receipt.add_discount(Discount(self.apples, "2 for 3.49", -0.49))
        verify(self.printer.print_receipt(self.receipt))

    def test_discount_five_for_amount(self):
        self.receipt.add_product(self.apples, 5, self.apples_price, 9.95)
        self.receipt.add_discount(Discount(self.apples, "5 for 9.0", -0.95))
        verify(self.printer.print_receipt(self.receipt))

    def test_multiple_discounts(self):
        self.receipt.add_product(self.toothbrush, 3, self.toothbrush_price, 3 * self.toothbrush_price)
        self.receipt.add_product(self.apples, 0.75, self.apples_price, 0.75 * self.apples_price)
        self.receipt.add_discount(Discount(self.toothbrush, "3 for 2", -0.99))
        self.receipt.add_discount(Discount(self.apples, "10.0% off", -0.15))
        verify(self.printer.print_receipt(self.receipt))
