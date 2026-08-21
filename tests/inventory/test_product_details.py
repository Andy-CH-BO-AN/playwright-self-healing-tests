from playwright.sync_api import Page, expect

from pages.inventory.inventory_page import InventoryPage
from pages.inventory.product_detail_page import ProductDetailPage

TARGET_PRODUCT = "Sauce Labs Backpack"


def test_product_details_match_inventory(logged_in_page: Page) -> None:
    inventory_page = InventoryPage(logged_in_page)
    detail_page = ProductDetailPage(logged_in_page)

    inventory_item = inventory_page.item_by_name(TARGET_PRODUCT)
    expected_name = inventory_item.name.inner_text()
    expected_description = inventory_item.description.inner_text()
    expected_price = inventory_item.price.inner_text()

    inventory_item.open()

    expect(detail_page.name).to_have_text(expected_name)
    expect(detail_page.description).to_have_text(expected_description)
    expect(detail_page.price).to_have_text(expected_price)
