from playwright.sync_api import Locator, Page


class InventoryPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.products_title: Locator = page.locator("[data-test='title']")
        self.shopping_cart_link: Locator = page.locator(
            "[data-test='shopping-cart-link']"
        )
        self.items: Locator = page.locator("[data-test='inventory-item']")

    def item_by_name(self, name: str) -> Locator:
        return self.items.filter(
            has=self.page.locator("[data-test='inventory-item-name']", has_text=name)
        )

    def add_to_cart(self, name: str) -> None:
        self.item_by_name(name).get_by_role("button", name="Add to cart").click()

    def open_product(self, name: str) -> None:
        self.item_by_name(name).locator("[data-test='inventory-item-name']").click()

    def open_cart(self) -> None:
        self.shopping_cart_link.click()
