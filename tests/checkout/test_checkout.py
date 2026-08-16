from decimal import Decimal

from playwright.sync_api import Page, expect

from config import Settings
from pages.authentication.login_page import LoginPage
from pages.cart.cart_page import CartPage
from pages.checkout.checkout_complete_page import CheckoutCompletePage
from pages.checkout.checkout_information_page import CheckoutInformationPage
from pages.checkout.checkout_overview_page import CheckoutOverviewPage, parse_price
from pages.inventory.inventory_page import InventoryPage


def test_user_can_complete_checkout(page: Page, settings: Settings) -> None:
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    cart_page = CartPage(page)
    checkout_info_page = CheckoutInformationPage(page)
    checkout_overview_page = CheckoutOverviewPage(page)
    checkout_complete_page = CheckoutCompletePage(page)

    login_page.open(settings.base_url)
    login_page.log_in(settings.standard_user.username, settings.standard_user.password)

    first_item = inventory_page.items.first
    product_name = first_item.locator("[data-test='inventory-item-name']").inner_text()
    product_price_text = first_item.locator(
        "[data-test='inventory-item-price']"
    ).inner_text()
    expected_product_price = parse_price(product_price_text)

    inventory_page.add_to_cart(product_name)
    inventory_page.open_cart()
    cart_page.proceed_to_checkout()

    checkout_info_page.fill_information("John", "Doe", "12345")

    overview_item = checkout_overview_page.item_by_name(product_name)
    expect(overview_item).to_be_visible()
    expect(overview_item.locator("[data-test='inventory-item-name']")).to_have_text(
        product_name
    )
    expect(overview_item.locator("[data-test='inventory-item-price']")).to_have_text(
        product_price_text
    )

    subtotal = checkout_overview_page.subtotal()
    tax = checkout_overview_page.tax()
    total = checkout_overview_page.total()

    assert subtotal == expected_product_price
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

    items = inventory_page.items.all()
    item_a, item_b = items[0], items[1]

    product_a_name = item_a.locator("[data-test='inventory-item-name']").inner_text()
    product_a_price_text = item_a.locator(
        "[data-test='inventory-item-price']"
    ).inner_text()
    product_a_price = parse_price(product_a_price_text)

    product_b_name = item_b.locator("[data-test='inventory-item-name']").inner_text()
    product_b_price_text = item_b.locator(
        "[data-test='inventory-item-price']"
    ).inner_text()
    product_b_price = parse_price(product_b_price_text)

    inventory_page.add_to_cart(product_a_name)
    inventory_page.add_to_cart(product_b_name)
    inventory_page.open_cart()

    cart_item_a = cart_page.item_by_name(product_a_name)
    cart_item_b = cart_page.item_by_name(product_b_name)

    expect(cart_item_a).to_be_visible()
    expect(cart_item_a.locator("[data-test='inventory-item-name']")).to_have_text(
        product_a_name
    )
    expect(cart_item_a.locator("[data-test='inventory-item-price']")).to_have_text(
        product_a_price_text
    )
    expect(cart_item_a.locator("[data-test='item-quantity']")).to_have_text("1")

    expect(cart_item_b).to_be_visible()
    expect(cart_item_b.locator("[data-test='inventory-item-name']")).to_have_text(
        product_b_name
    )
    expect(cart_item_b.locator("[data-test='inventory-item-price']")).to_have_text(
        product_b_price_text
    )
    expect(cart_item_b.locator("[data-test='item-quantity']")).to_have_text("1")

    cart_page.proceed_to_checkout()
    checkout_info_page.fill_information("Jane", "Smith", "90210")

    overview_item_a = checkout_overview_page.item_by_name(product_a_name)
    overview_item_b = checkout_overview_page.item_by_name(product_b_name)

    expect(overview_item_a).to_be_visible()
    expect(overview_item_a.locator("[data-test='inventory-item-name']")).to_have_text(
        product_a_name
    )
    expect(overview_item_a.locator("[data-test='inventory-item-price']")).to_have_text(
        product_a_price_text
    )
    expect(overview_item_a.locator("[data-test='item-quantity']")).to_have_text("1")

    expect(overview_item_b).to_be_visible()
    expect(overview_item_b.locator("[data-test='inventory-item-name']")).to_have_text(
        product_b_name
    )
    expect(overview_item_b.locator("[data-test='inventory-item-price']")).to_have_text(
        product_b_price_text
    )
    expect(overview_item_b.locator("[data-test='item-quantity']")).to_have_text("1")

    subtotal = checkout_overview_page.subtotal()
    tax = checkout_overview_page.tax()
    total = checkout_overview_page.total()

    assert subtotal == product_a_price + product_b_price
    assert tax > Decimal("0.00")
    assert total == subtotal + tax
