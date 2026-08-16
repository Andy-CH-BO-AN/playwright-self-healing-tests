from playwright.sync_api import Page, expect

from config import Settings
from pages.authentication.login_page import LoginPage
from pages.cart.cart_page import CartPage
from pages.inventory.inventory_page import InventoryPage
from pages.inventory.product_detail_page import ProductDetailPage


def test_product_added_from_inventory_appears_in_cart(
    page: Page, settings: Settings
) -> None:
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    cart_page = CartPage(page)

    login_page.open(settings.base_url)
    login_page.log_in(settings.standard_user.username, settings.standard_user.password)

    first_item = inventory_page.items.first
    product_name = first_item.locator("[data-test='inventory-item-name']").inner_text()
    product_price = first_item.locator(
        "[data-test='inventory-item-price']"
    ).inner_text()

    inventory_page.add_to_cart(product_name)
    inventory_page.open_cart()

    cart_item = cart_page.item_by_name(product_name)
    expect(cart_item).to_be_visible()
    expect(cart_item.locator("[data-test='inventory-item-name']")).to_have_text(
        product_name
    )
    expect(cart_item.locator("[data-test='inventory-item-price']")).to_have_text(
        product_price
    )
    expect(cart_item.locator("[data-test='item-quantity']")).to_have_text("1")


def test_product_added_from_detail_appears_in_cart(
    page: Page, settings: Settings
) -> None:
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    detail_page = ProductDetailPage(page)
    cart_page = CartPage(page)

    login_page.open(settings.base_url)
    login_page.log_in(settings.standard_user.username, settings.standard_user.password)

    first_item = inventory_page.items.first
    product_name = first_item.locator("[data-test='inventory-item-name']").inner_text()
    product_price = first_item.locator(
        "[data-test='inventory-item-price']"
    ).inner_text()

    inventory_page.open_product(product_name)
    detail_page.add_to_cart()
    detail_page.open_cart()

    cart_item = cart_page.item_by_name(product_name)
    expect(cart_item).to_be_visible()
    expect(cart_item.locator("[data-test='inventory-item-name']")).to_have_text(
        product_name
    )
    expect(cart_item.locator("[data-test='inventory-item-price']")).to_have_text(
        product_price
    )
    expect(cart_item.locator("[data-test='item-quantity']")).to_have_text("1")
