import re
from decimal import Decimal

from playwright.sync_api import Locator, Page


def parse_price(text: str) -> Decimal:
    match = re.search(r"\$([\d.]+)", text)
    if not match:
        raise ValueError(f"Could not extract monetary value from '{text}'")
    return Decimal(match.group(1))


class CheckoutOverviewPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.title: Locator = page.locator("[data-test='title']")
        self.items: Locator = page.locator("[data-test='inventory-item']")
        self.subtotal_label: Locator = page.locator("[data-test='subtotal-label']")
        self.tax_label: Locator = page.locator("[data-test='tax-label']")
        self.total_label: Locator = page.locator("[data-test='total-label']")
        self.finish_button: Locator = page.get_by_role("button", name="Finish")
        self.cancel_button: Locator = page.get_by_role("button", name="Cancel")

    def item_by_name(self, name: str) -> Locator:
        return self.items.filter(
            has=self.page.locator("[data-test='inventory-item-name']", has_text=name)
        )

    def subtotal(self) -> Decimal:
        return parse_price(self.subtotal_label.inner_text())

    def tax(self) -> Decimal:
        return parse_price(self.tax_label.inner_text())

    def total(self) -> Decimal:
        return parse_price(self.total_label.inner_text())

    def finish(self) -> None:
        self.finish_button.click()
