from playwright.sync_api import Page, expect

from config import Settings
from pages.authentication.login_page import LoginPage
from pages.inventory.inventory_page import InventoryPage
from pages.inventory.product_detail_page import ProductDetailPage


def test_product_details_match_inventory(page: Page, settings: Settings) -> None:
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    detail_page = ProductDetailPage(page)

    login_page.open(settings.base_url)
    login_page.log_in(settings.standard_user.username, settings.standard_user.password)

    first_item = inventory_page.items.first
    expected_name = first_item.locator("[data-test='inventory-item-name']").inner_text()
    expected_description = first_item.locator(
        "[data-test='inventory-item-desc']"
    ).inner_text()
    expected_price = first_item.locator(
        "[data-test='inventory-item-price']"
    ).inner_text()

    inventory_page.open_product(expected_name)

    expect(detail_page.name).to_have_text(expected_name)
    expect(detail_page.description).to_have_text(expected_description)
    expect(detail_page.price).to_have_text(expected_price)
