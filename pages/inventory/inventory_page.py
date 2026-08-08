from playwright.sync_api import Locator, Page


class InventoryPage:
    def __init__(self, page: Page) -> None:
        self.products_title: Locator = page.locator("[data-test='title']")
