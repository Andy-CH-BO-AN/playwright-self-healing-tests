from decimal import Decimal

from playwright.sync_api import Page, expect

from config import Settings
from pages.authentication.login_page import LoginPage
from pages.cart.cart_page import CartPage
from pages.checkout.checkout_complete_page import CheckoutCompletePage
from pages.checkout.checkout_information_page import CheckoutInformationPage
from pages.checkout.checkout_overview_page import CheckoutOverviewPage
from pages.inventory.inventory_page import InventoryPage

PRODUCT_A = "Sauce Labs Backpack"
PRODUCT_B = "Sauce Labs Bike Light"


def test_user_can_complete_checkout(page: Page, settings: Settings) -> None:
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    cart_page = CartPage(page)
    checkout_info_page = CheckoutInformationPage(page)
    checkout_overview_page = CheckoutOverviewPage(page)
    checkout_complete_page = CheckoutCompletePage(page)

    login_page.open(settings.base_url)
    login_page.log_in(settings.standard_user.username, settings.standard_user.password)

    inventory_item = inventory_page.item_by_name(PRODUCT_A)
    expected_name = inventory_item.name.inner_text()
    expected_price_text = inventory_item.price.inner_text()
    expected_price = inventory_item.price_value()

    inventory_item.add_to_cart()
    inventory_page.open_cart()
    cart_page.proceed_to_checkout()

    checkout_info_page.fill_information("John", "Doe", "12345")

    overview_item = checkout_overview_page.item_by_name(PRODUCT_A)
    expect(overview_item.root).to_be_visible()
    expect(overview_item.name).to_have_text(expected_name)
    expect(overview_item.price).to_have_text(expected_price_text)

    subtotal = checkout_overview_page.subtotal()
    tax = checkout_overview_page.tax()
    total = checkout_overview_page.total()

    assert subtotal == expected_price
    assert tax > Decimal("0.00")
    assert total == subtotal + tax

    checkout_overview_page.finish()

    expect(checkout_complete_page.complete_header).to_be_visible()
    expect(checkout_complete_page.complete_header).to_have_text(
        "Thank you for your order!"
    )


def test_checkout_calculates_multiple_products_correctly(
    page: Page, settings: Settings
) -> None:
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    cart_page = CartPage(page)
    checkout_info_page = CheckoutInformationPage(page)
    checkout_overview_page = CheckoutOverviewPage(page)

    login_page.open(settings.base_url)
    login_page.log_in(settings.standard_user.username, settings.standard_user.password)

    item_a = inventory_page.item_by_name(PRODUCT_A)
    item_b = inventory_page.item_by_name(PRODUCT_B)

    product_a_name = item_a.name.inner_text()
    product_a_price_text = item_a.price.inner_text()
    product_a_price = item_a.price_value()

    product_b_name = item_b.name.inner_text()
    product_b_price_text = item_b.price.inner_text()
    product_b_price = item_b.price_value()

    item_a.add_to_cart()
    item_b.add_to_cart()
    inventory_page.open_cart()

    cart_item_a = cart_page.item_by_name(PRODUCT_A)
    cart_item_b = cart_page.item_by_name(PRODUCT_B)

    expect(cart_item_a.root).to_be_visible()
    expect(cart_item_a.name).to_have_text(product_a_name)
    expect(cart_item_a.price).to_have_text(product_a_price_text)
    expect(cart_item_a.quantity).to_have_text("1")

    expect(cart_item_b.root).to_be_visible()
    expect(cart_item_b.name).to_have_text(product_b_name)
    expect(cart_item_b.price).to_have_text(product_b_price_text)
    expect(cart_item_b.quantity).to_have_text("1")

    cart_page.proceed_to_checkout()
    checkout_info_page.fill_information("Jane", "Smith", "90210")

    overview_item_a = checkout_overview_page.item_by_name(PRODUCT_A)
    overview_item_b = checkout_overview_page.item_by_name(PRODUCT_B)

    expect(overview_item_a.root).to_be_visible()
    expect(overview_item_a.name).to_have_text(product_a_name)
    expect(overview_item_a.price).to_have_text(product_a_price_text)
    expect(overview_item_a.quantity).to_have_text("1")

    expect(overview_item_b.root).to_be_visible()
    expect(overview_item_b.name).to_have_text(product_b_name)
    expect(overview_item_b.price).to_have_text(product_b_price_text)
    expect(overview_item_b.quantity).to_have_text("1")

    subtotal = checkout_overview_page.subtotal()
    tax = checkout_overview_page.tax()
    total = checkout_overview_page.total()

    assert subtotal == product_a_price + product_b_price
    assert tax > Decimal("0.00")
    assert total == subtotal + tax
