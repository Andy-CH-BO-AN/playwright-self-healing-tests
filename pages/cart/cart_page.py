from playwright.sync_api import Locator, Page


class CartItem:
    def __init__(self, locator: Locator) -> None:
        self.root: Locator = locator
        self.name: Locator = locator.locator("[data-test='inventory-item-name']")
        self.description: Locator = locator.locator("[data-test='inventory-item-description']")
        self.price: Locator = locator.locator("[data-test='inventory-item-price']")
        self.quantity: Locator = locator.locator("[data-test='item-quantity']")
        self.remove_button: Locator = locator.get_by_role("button", name="Remove")


class CartPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.title: Locator = page.locator("[data-test='title']")
        self.items: Locator = page.locator("[data-test='inventory-item']")
        self.checkout_button: Locator = page.get_by_role("button", name="Checkout")

    def item_by_name(self, name: str) -> CartItem:
        locator = self.items.filter(
            has=self.page.locator("[data-test='inventory-item-name']").get_by_text(
                name, exact=True
            )
        )
        return CartItem(locator)

    def proceed_to_checkout(self) -> None:
        self.checkout_button.click()
