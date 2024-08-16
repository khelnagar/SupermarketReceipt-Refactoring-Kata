# helper file to use the supermarket


from model_objects import Product, SpecialOfferType, ProductUnit
from receipt_printer import ReceiptPrinter
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


catalog = FakeCatalog()
toothbrush = Product("toothbrush", ProductUnit.EACH)
catalog.add_product(toothbrush, 0.99)

apples = Product("apples", ProductUnit.KILO)
catalog.add_product(apples, 1.99)

teller = Teller(catalog)
teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, apples, 10.0)
teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0.99)

cart = ShoppingCart()
cart.add_item_quantity(apples, 0.75)
cart.add_item_quantity(toothbrush, 3)

receipt = teller.checks_out_articles_from(cart)
print(ReceiptPrinter(40).print_receipt(receipt))
