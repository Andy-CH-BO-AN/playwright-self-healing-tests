import json
import re
import traceback
from collections.abc import Callable
from pathlib import Path

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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()

    if report.failed and report.when in ("setup", "call"):
        try:
            slug = re.sub(r"[^\w\-.]+", "_", report.nodeid).strip("_")
            evidence_dir = Path("test-results/self-heal") / slug
            evidence_dir.mkdir(parents=True, exist_ok=True)

            error_type = ""
            error_message = ""
            tb_str = ""

            if call.excinfo is not None:
                error_type = getattr(
                    call.excinfo.type, "__name__", str(call.excinfo.type)
                )
                error_message = str(call.excinfo.value)
                tb_str = "".join(
                    traceback.format_exception(
                        call.excinfo.type,
                        call.excinfo.value,
                        call.excinfo.tb,
                    )
                )
            elif report.longrepr:
                tb_str = str(report.longrepr)

            page: Page | None = None
            if hasattr(item, "funcargs"):
                for arg in item.funcargs.values():
                    if isinstance(arg, Page):
                        page = arg
                        break

            url = ""
            html_content = ""
            if page is not None:
                try:
                    url = page.url
                    html_content = page.content()
                except Exception:
                    pass

            failure_data = {
                "nodeid": report.nodeid,
                "phase": report.when,
                "error_type": error_type,
                "error_message": error_message,
                "traceback": tb_str,
                "url": url,
            }

            (evidence_dir / "failure.json").write_text(
                json.dumps(failure_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            if html_content:
                (evidence_dir / "page.html").write_text(
                    html_content,
                    encoding="utf-8",
                )
        except Exception:
            pass
