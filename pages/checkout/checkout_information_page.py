from playwright.sync_api import Locator, Page


class CheckoutInformationPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.title: Locator = page.locator("[data-test='title']")
        self.first_name_input: Locator = page.get_by_placeholder("First Name")
        self.last_name_input: Locator = page.get_by_placeholder("Last Name")
        self.postal_code_input: Locator = page.get_by_placeholder("Zip/Postal Code")
        self.continue_button: Locator = page.get_by_role("button", name="Continue")
        self.cancel_button: Locator = page.get_by_role("button", name="Cancel")

    def fill_information(
        self, first_name: str, last_name: str, postal_code: str
    ) -> None:
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(postal_code)
        self.continue_button.click()
