import re
from decimal import Decimal

from playwright.sync_api import Locator, Page


def _extract_amount(text: str) -> Decimal:
    match = re.search(r"\$([\d.]+)", text)
    if not match:
        raise ValueError(f"Could not extract monetary value from '{text}'")
    return Decimal(match.group(1))


class OverviewItem:
    def __init__(self, locator: Locator) -> None:
        self.root: Locator = locator
        self.name: Locator = locator.locator("[data-test='inventory-item-name']")
        self.description: Locator = locator.locator("[data-test='inventory-item-desc']")
        self.price: Locator = locator.locator("[data-test='inventory-item-price']")
        self.quantity: Locator = locator.locator("[data-test='item-quantity']")


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

    def item_by_name(self, name: str) -> OverviewItem:
        locator = self.items.filter(
            has=self.page.locator("[data-test='inventory-item-name']", has_text=name)
        )
        return OverviewItem(locator)

    def subtotal(self) -> Decimal:
        return _extract_amount(self.subtotal_label.inner_text())

    def tax(self) -> Decimal:
        return _extract_amount(self.tax_label.inner_text())

    def total(self) -> Decimal:
        return _extract_amount(self.total_label.inner_text())

    def finish(self) -> None:
        self.finish_button.click()
