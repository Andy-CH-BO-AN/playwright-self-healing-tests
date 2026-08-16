from playwright.sync_api import Locator, Page


class CheckoutCompletePage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.title: Locator = page.locator("[data-test='title']")
        self.complete_header: Locator = page.locator("[data-test='complete-header']")
        self.complete_text: Locator = page.locator("[data-test='complete-text']")
        self.back_home_button: Locator = page.locator("[data-test='back-to-products']")
