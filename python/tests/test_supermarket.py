import unittest
import pytest

from model_objects import Product, SpecialOfferType, ProductUnit, ProductQuantity
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


def approximate_equal(n, approx=0.01):
    return pytest.approx(n, approx)


class ShoppingCartTest(unittest.TestCase):
    def setUp(self):
        self.catalog = FakeCatalog()
        self.cart = ShoppingCart()
        self.teller = Teller(self.catalog)

        self.toothbrush = Product("toothbrush", ProductUnit.EACH)
        self.catalog.add_product(self.toothbrush, 0.99)

        self.apples = Product("apples", ProductUnit.KILO)
        self.catalog.add_product(self.apples, 1.99)

        self.tea_bag = Product("tea bag", ProductUnit.EACH)
        self.catalog.add_product(self.tea_bag, 0.79)

        self.rice = Product("rice", ProductUnit.KILO)
        self.catalog.add_product(self.rice, 1.49)

        self.toothbrush_price = self.catalog.unit_price(self.toothbrush)
        self.apples_price = self.catalog.unit_price(self.apples)
        self.tea_bag_price = self.catalog.unit_price(self.tea_bag)
        self.rice_price = self.catalog.unit_price(self.rice)

    def test_no_items_zero_cost(self):
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 0

    def test_one_item(self):
        self.cart.add_item(self.tea_bag)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert len(receipt.items) == 1
        receipt_item = receipt.items[0]
        assert receipt_item.product == self.tea_bag
        assert receipt_item.price == self.tea_bag_price
        assert approximate_equal(receipt_item.total_price) == self.tea_bag_price
        assert receipt_item.quantity == 1
        assert approximate_equal(receipt.total_price()) == self.tea_bag_price
        assert self.cart.product_quantities == {self.tea_bag: 1}

    def test_two_similar_items(self):
        self.cart.add_item(self.tea_bag)
        self.cart.add_item(self.tea_bag)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 2 * self.tea_bag_price

    def test_three_items(self):
        self.cart.add_item(self.tea_bag)
        self.cart.add_item(self.apples)
        self.cart.add_item(self.toothbrush)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert (
            approximate_equal(receipt.total_price()) == self.tea_bag_price + self.apples_price + self.toothbrush_price
        )

    def test_fraction_kilo(self):
        self.cart.add_item_quantity(self.apples, 0.75)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 0.75 * self.apples_price

    def test_offer_exists_but_no_discount(self):
        self.teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, self.apples, 10.0)
        self.cart.add_item(self.toothbrush)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == self.toothbrush_price
        assert receipt.discounts == []

    def test_percent_discount_one_item(self):
        self.teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, self.apples, 10.0)
        self.cart.add_item(self.apples)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 0.9 * self.apples_price

    def test_same_percent_discount_all_items(self):
        self.teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, self.apples, 10.0)
        self.teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, self.toothbrush, 10.0)
        self.cart.add_item(self.apples)
        self.cart.add_item(self.toothbrush)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 0.9 * (self.apples_price + self.toothbrush_price)

    def test_three_for_two_unit(self):
        self.teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, self.toothbrush, self.toothbrush_price)
        self.cart.add_item(self.toothbrush)
        self.cart.add_item(self.toothbrush)
        self.cart.add_item(self.toothbrush)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 2 * self.toothbrush_price

    def test_three_for_two_kilo(self):
        self.teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, self.apples, self.apples_price)
        self.cart.add_item_quantity(self.apples, 3)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 2 * self.apples_price

    def test_five_for_four(self):
        self.teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, self.toothbrush, self.toothbrush_price)
        self.cart.add_item_quantity(self.toothbrush, 5)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 4 * self.toothbrush_price

    def test_six_for_four(self):
        # this proves buying 6 is better than buying 5
        self.teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, self.toothbrush, self.toothbrush_price)
        self.cart.add_item_quantity(self.toothbrush, 6)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 4 * self.toothbrush_price

    def test_two_for_amount(self):
        self.teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, self.tea_bag, 1.24)
        self.cart.add_item(self.tea_bag)
        self.cart.add_item(self.tea_bag)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 1.24
        assert (
            approximate_equal(abs(sum([i.discount_amount for i in receipt.discounts]))) == 2 * self.tea_bag_price - 1.24
        )

    def test_five_for_amount(self):
        self.teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, self.apples, 6.99)
        self.cart.add_item_quantity(self.apples, 5)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 6.99
        assert (
            approximate_equal(abs(sum([i.discount_amount for i in receipt.discounts]))) == 5 * self.apples_price - 6.99
        )

    def test_five_for_amount_with_less_than_five(self):
        self.teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, self.apples, 6.99)
        self.cart.add_item_quantity(self.apples, 4)
        receipt = self.teller.checks_out_articles_from(self.cart)
        assert approximate_equal(receipt.total_price()) == 4 * self.apples_price
        assert approximate_equal(abs(sum([i.discount_amount for i in receipt.discounts]))) == 0

    def test_five_for_amount_with_multiple_fives(self):
        self.teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, self.apples, 6.99)
        self.cart.add_item_quantity(self.apples, 11)
        receipt = self.teller.checks_out_articles_from(self.cart)
        discounted_price = 2 * 6.99 + self.apples_price
        assert approximate_equal(receipt.total_price()) == discounted_price
        assert (
            approximate_equal(abs(sum([i.discount_amount for i in receipt.discounts])))
            == 11 * self.apples_price - discounted_price
        )

    def test_all_offers(self):
        self.teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, self.toothbrush, 10.0)
        self.teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, self.tea_bag, self.tea_bag_price)
        self.teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, self.apples, 2.99)
        self.teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, self.rice, 4.99)

        self.cart.add_item_quantity(self.toothbrush, 1)
        self.cart.add_item_quantity(self.tea_bag, 3)
        self.cart.add_item_quantity(self.apples, 2)
        self.cart.add_item_quantity(self.rice, 5)

        receipt = self.teller.checks_out_articles_from(self.cart)
        discounted_price = 4.99 + 2.99 + 2 * self.tea_bag_price + 0.9 * self.toothbrush_price
        actual_price = self.toothbrush_price + 3 * self.tea_bag_price + 2 * self.apples_price + 5 * self.rice_price
        assert approximate_equal(receipt.total_price()) == discounted_price
        assert (
            approximate_equal(abs(sum([i.discount_amount for i in receipt.discounts])))
            == actual_price - discounted_price
        )
