from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

DEFAULT_BASE_URL = "https://www.saucedemo.com"


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str


@dataclass(frozen=True)
class Settings:
    base_url: str
    standard_user: Credentials


def _required_environment_variable(name: str) -> str:
    value = getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set in the environment or .env file")
    return value


def load_settings() -> Settings:
    load_dotenv()
    base_url = getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    return Settings(
        base_url=base_url,
        standard_user=Credentials(
            username=_required_environment_variable("SAUCEDEMO_USERNAME"),
            password=_required_environment_variable("SAUCEDEMO_PASSWORD"),
        ),
    )
