from playwright.sync_api import Page, expect

from config import Settings
from pages.authentication.login_page import LoginPage
from pages.inventory.inventory_page import InventoryPage


def test_standard_user_can_log_in(page: Page, settings: Settings) -> None:
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)

    login_page.open(settings.base_url)
    login_page.log_in(settings.standard_user.username, settings.standard_user.password)

    expect(inventory_page.products_title).to_be_visible()
    expect(inventory_page.products_title).to_have_text("Products")
