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

### Native Local Debug

本機環境快速開發與逐步除錯：

```bash
ruff check .
ruff format --check .
pytest --browser chromium
```

或以 2 workers 本機平行執行：

```bash
pytest --browser chromium -n 2
```

- 平行執行透過 `pytest-xdist` 分派至 2 個 worker processes。
- 每個 testcase 維持獨立 `BrowserContext` 與 Page 生命週期，確保 shopping cart 與 session state 互相隔離。
- 未指定 `-n` 時預設為 serial execution，便於 local 逐步除錯與單一測試執行。

若需測試其他部署環境：

```bash
BASE_URL=https://www.saucedemo.com pytest --browser chromium -n 2
```

## Reproducible Container Execution

Docker 作為此測試套件的 canonical reproducible execution environment。Container 內已包含完整的 source code 與 Playwright 執行環境，不依賴 host source bind mount。

### Build Image

```bash
docker compose build tests
```

### Run Suite in Container

```bash
docker compose run --rm tests
```

- Container 預設以 2 workers 平行執行完整 suite (`pytest --browser chromium -n 2`)。
- 程式碼修改後需透過 `docker compose build tests` 重新打包進 image。
- 僅 `./test-results` 掛載至 host，確保測試失敗時的 screenshot 與 trace 能正常輸出至本機。
- 執行 Ruff 檢查：
  ```bash
  docker compose run --rm tests ruff check .
  docker compose run --rm tests ruff format --check .
  ```

## GitHub Actions

Pull request 與 main branch push 均在 `ubuntu-24.04` runner 上以 Docker 容器化流程執行，與 local container 執行路徑完全一致：

1. 建置 repository Docker image (`docker compose build tests`)。
2. 在 container 內執行 Ruff 語法與排版檢查。
3. 在 container 內以 2 workers 平行執行完整 Playwright E2E suite (`pytest --browser chromium -n 2`)。
4. 測試失敗時，透過 volume mount 持久化至 runner 的 `test-results/` 並自動上傳為 artifact。
5. GitHub Actions workflow 的 action dependencies (`actions/checkout`, `actions/upload-artifact`) 皆以 full commit SHA 固定，強化供應鏈安全。

## Roadmap

- [x] Phase 1 — Framework + Login happy path
- [x] Phase 2 — Core E2E scenarios
- [x] Phase 3 — Parallel execution
- [x] Phase 4 — Docker / CI hardening
- [ ] Phase 5 — AI-assisted self-healing + Draft PR automation

