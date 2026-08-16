import re
from decimal import Decimal

from playwright.sync_api import Locator, Page


def parse_price(text: str) -> Decimal:
    match = re.search(r"\$([\d.]+)", text)
    if not match:
        raise ValueError(f"Could not extract monetary value from '{text}'")
    return Decimal(match.group(1))


class InventoryItem:
    def __init__(self, locator: Locator) -> None:
        self.root: Locator = locator
        self.name: Locator = locator.locator("[data-test='inventory-item-name']")
        self.description: Locator = locator.locator("[data-test='inventory-item-desc']")
        self.price: Locator = locator.locator("[data-test='inventory-item-price']")
        self.add_to_cart_button: Locator = locator.get_by_role(
            "button", name="Add to cart"
        )

    def open(self) -> None:
        self.name.click()

    def add_to_cart(self) -> None:
        self.add_to_cart_button.click()

    def price_value(self) -> Decimal:
        return parse_price(self.price.inner_text())


class InventoryPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.products_title: Locator = page.locator("[data-test='title']")
        self.shopping_cart_link: Locator = page.locator(
            "[data-test='shopping-cart-link']"
        )
        self.items: Locator = page.locator("[data-test='inventory-item']")

    def item_by_name(self, name: str) -> InventoryItem:
        locator = self.items.filter(
            has=self.page.locator("[data-test='inventory-item-name']").get_by_text(
                name, exact=True
            )
        )
        return InventoryItem(locator)

    def open_cart(self) -> None:
        self.shopping_cart_link.click()
