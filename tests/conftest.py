from collections.abc import Callable

import pytest
from playwright.sync_api import Page

from config import Settings, load_settings
from pages.authentication.login_page import LoginPage


@pytest.fixture(scope="session")
def settings() -> Settings:
    return load_settings()


@pytest.fixture
def login_as(page: Page, settings: Settings) -> Callable[..., Page]:
    def _login(
        username: str | None = None,
        password: str | None = None,
    ) -> Page:
        user = username or settings.standard_user.username
        pwd = password or settings.standard_user.password

        login_page = LoginPage(page)
        login_page.open(settings.base_url)
        login_page.log_in(user, pwd)
        return page

    return _login


@pytest.fixture
def logged_in_page(login_as: Callable[..., Page]) -> Page:
    return login_as()
