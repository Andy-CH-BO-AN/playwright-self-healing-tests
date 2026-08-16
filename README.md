# Playwright Self-Healing Tests

供維護此測試套件的工程師，以 Python、pytest 與 Playwright 建立可維護的 SauceDemo E2E 測試基礎。

## 技術棧

- Python 3.14
- pytest、pytest-playwright、pytest-xdist、Playwright Python、python-dotenv
- Ruff
- Docker Compose
- GitHub Actions

## Architecture

- pytest-playwright 管理 Chromium、BrowserContext 與 Page 生命週期；每個 testcase 使用獨立 context/page。
- Page Object 集中頁面 locator 與使用者互動；testcase 保留登入流程與使用者可觀察的 assertion。SauceDemo 的 Products title 使用穩定 `data-test="title"` contract。
- `config.py` 集中 Base URL 與登入帳密。可用環境變數覆寫；local run 從 `.env` 載入。
- `.env` 不納入版本控制；`.env.example` 僅提供 credential placeholder，local run 需填入自己的 SauceDemo 帳密。
- 失敗時保留 full-page screenshot 與 Playwright trace；passing test 不保留這些 artifact。

## Project Structure

```text
config.py
pages/
  authentication/login_page.py
  cart/cart_page.py
  checkout/
    checkout_complete_page.py
    checkout_information_page.py
    checkout_overview_page.py
  inventory/
    inventory_page.py
    product_detail_page.py
tests/
  conftest.py
  authentication/test_login.py
  cart/test_cart.py
  checkout/test_checkout.py
  inventory/test_product_details.py
```

## Local Setup

```bash
python3.14 -m venv .venv
source .venv/bin/activate
cp .env.example .env
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

建立 `.env` 後，將 `SAUCEDEMO_USERNAME` 與 `SAUCEDEMO_PASSWORD` placeholder 改成自己的測試帳密。

## Run Tests

### Serial Execution (Local Debug)

```bash
ruff check .
ruff format --check .
pytest --browser chromium
```

### Parallel Execution (Standard / CI)

```bash
pytest --browser chromium -n 2
```

- 平行執行透過 `pytest-xdist` 分派至 2 個 worker processes。
- 每個 testcase 維持獨立 `BrowserContext` 與 Page 生命週期，確保 shopping cart 與 session state 互相隔離。
- CI 預設使用 2 workers 執行完整 parallel suite。
- 未指定 `-n` 時預設為 serial execution，便於 local 逐步除錯與單一測試執行。

若需測試其他部署環境：

```bash
BASE_URL=https://www.saucedemo.com pytest --browser chromium -n 2
```

## Docker

Docker image 使用官方 Playwright Python `v1.61.0-resolute` image（Ubuntu 26.04 LTS），與 pinned Playwright Python package 版本一致，並將 local、CI 與 container runtime 對齊 Python 3.14。Local `.env` 不會被複製進 Docker image；Docker Compose 僅在執行時傳入需要的環境變數。

```bash
docker compose run --rm tests
```

## GitHub Actions

Pull request 與 main branch push 會使用 Python 3.14 安裝 dependencies、Chromium、執行 Ruff 與以 2 workers 平行執行完整 Playwright E2E suite (`pytest --browser chromium -n 2`)。CI 的 `SAUCEDEMO_USERNAME` 與 `SAUCEDEMO_PASSWORD` 由 GitHub Actions Secrets 注入；失敗時上傳 `test-results/`，供下載 screenshot 與 trace。

## Roadmap

- [x] Phase 1 — Framework + Login happy path
- [x] Phase 2 — Core E2E scenarios
- [x] Phase 3 — Parallel execution
- [ ] Phase 4 — Docker / CI hardening
- [ ] Phase 5 — AI-assisted self-healing + Draft PR automation

