from playwright.sync_api import Locator, Page


class ProductDetailPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.name: Locator = page.locator("[data-test='inventory-item-name']")
        self.description: Locator = page.locator("[data-test='inventory-item-desc']")
        self.price: Locator = page.locator("[data-test='inventory-item-price']")
        self.add_to_cart_button: Locator = page.get_by_role(
            "button", name="Add to cart"
        )
        self.shopping_cart_link: Locator = page.locator(
            "[data-test='shopping-cart-link']"
        )
        self.back_to_products_button: Locator = page.locator(
            "[data-test='back-to-products']"
        )

    def add_to_cart(self) -> None:
        self.add_to_cart_button.click()

    def open_cart(self) -> None:
        self.shopping_cart_link.click()
