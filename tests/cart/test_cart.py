from playwright.sync_api import Page, expect

from pages.cart.cart_page import CartPage
from pages.inventory.inventory_page import InventoryPage
from pages.inventory.product_detail_page import ProductDetailPage

TARGET_PRODUCT = "Sauce Labs Backpack"


def test_product_added_from_inventory_appears_in_cart(
    logged_in_page: Page,
) -> None:
    inventory_page = InventoryPage(logged_in_page)
    cart_page = CartPage(logged_in_page)

    inventory_item = inventory_page.item_by_name(TARGET_PRODUCT)
    expected_name = inventory_item.name.inner_text()
    expected_price = inventory_item.price.inner_text()

    inventory_item.add_to_cart()
    inventory_page.open_cart()

    cart_item = cart_page.item_by_name(TARGET_PRODUCT)
    expect(cart_item.root).to_be_visible()
    expect(cart_item.name).to_have_text(expected_name)
    expect(cart_item.price).to_have_text(expected_price)
    expect(cart_item.quantity).to_have_text("1")


def test_product_added_from_detail_appears_in_cart(
    logged_in_page: Page,
) -> None:
    inventory_page = InventoryPage(logged_in_page)
    detail_page = ProductDetailPage(logged_in_page)
    cart_page = CartPage(logged_in_page)

    inventory_item = inventory_page.item_by_name(TARGET_PRODUCT)
    expected_name = inventory_item.name.inner_text()
    expected_price = inventory_item.price.inner_text()

    inventory_item.open()
    detail_page.add_to_cart()
    detail_page.open_cart()

    cart_item = cart_page.item_by_name(TARGET_PRODUCT)
    expect(cart_item.root).to_be_visible()
    expect(cart_item.name).to_have_text(expected_name)
    expect(cart_item.price).to_have_text(expected_price)
    expect(cart_item.quantity).to_have_text("1")
