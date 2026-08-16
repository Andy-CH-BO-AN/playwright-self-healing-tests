from playwright.sync_api import Locator, Page


class CartPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.title: Locator = page.locator("[data-test='title']")
        self.items: Locator = page.locator("[data-test='inventory-item']")
        self.checkout_button: Locator = page.get_by_role("button", name="Checkout")

    def item_by_name(self, name: str) -> Locator:
        return self.items.filter(
            has=self.page.locator("[data-test='inventory-item-name']", has_text=name)
        )

    def proceed_to_checkout(self) -> None:
        self.checkout_button.click()
