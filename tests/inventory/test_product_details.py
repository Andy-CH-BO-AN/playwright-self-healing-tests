from playwright.sync_api import Page, expect

from config import Settings
from pages.authentication.login_page import LoginPage
from pages.inventory.inventory_page import InventoryPage
from pages.inventory.product_detail_page import ProductDetailPage

TARGET_PRODUCT = "Sauce Labs Backpack"


def test_product_details_match_inventory(page: Page, settings: Settings) -> None:
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)
    detail_page = ProductDetailPage(page)

    login_page.open(settings.base_url)
    login_page.log_in(settings.standard_user.username, settings.standard_user.password)

    inventory_item = inventory_page.item_by_name(TARGET_PRODUCT)
    expected_name = inventory_item.name.inner_text()
    expected_description = inventory_item.description.inner_text()
    expected_price = inventory_item.price.inner_text()

    inventory_item.open()

    expect(detail_page.name).to_have_text(expected_name)
    expect(detail_page.description).to_have_text(expected_description)
    expect(detail_page.price).to_have_text(expected_price)
