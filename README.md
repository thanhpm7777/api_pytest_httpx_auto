# API QA Suite

A company‑style API test suite featuring:
- **pytest + httpx** (fast API tests, fixtures, parallelism)
- **Allure** (rich HTML reports)
- **Schemathesis** (schema/property tests from OpenAPI)
- **Pact** (contract tests, consumer first)
- **Locust** (performance smoke & load)
- **GitHub Actions** (CI ready)

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill BASE_URL, USERNAME, PASSWORD, API_SCHEMA_URL
pytest -n auto
```

### Run selected suites
```bash
pytest -m smoke
pytest -m regression
pytest -m schemathesis
pytest -m contract tests/contract/consumer
locust -f performance/locustfile.py --host=http://localhost:8000
```

### Allure
```bash
pytest --alluredir=reports/allure
allure serve reports/allure
```

### Docker
```bash
docker compose build
docker compose run --rm tests
# Locust UI
docker compose up locust  # open http://localhost:8089
```

## Customizing endpoints
Edit `.env` paths if your API uses different URLs (e.g. `/api/v1/auth/jwt/create/`).

## Tokens in tests (best practice)
- Use a dedicated **test user** with least privilege; rotate creds.
- Avoid calling register/login for every test; cache a token per test session (see `tests/utils/auth.py`).
- For negative tests, create explicit fixtures with invalid/expired tokens.

## Schemathesis
Set `API_SCHEMA_URL` to your OpenAPI (JSON/YAML). Tests will generate data and validate responses.

## Contract testing (Pact)
- Consumer tests produce pact files in `pact/pacts`.
- Provider service should verify those pacts in its own CI (see `tests/contract/provider/README.md`).

## Performance
Locust users simulate common flows (list/create blogs). Tune users (`-u`), spawn rate (`-r`) and time (`-t`).

## CI
`ci.yml` runs: functional tests, schemathesis (separate job), and contract tests. Allure results & pact files uploaded as artifacts.
```

---

## Notes
- Markers provide clean separation for **smoke**, **regression**, **schema**, **contract**, **perf**.
- Everything is environment‑driven; no hard‑coded host.
- Swap `requests` for `httpx` anywhere if you prefer unified client; Pact example uses `requests` due to current pact‑python docs, but you can proxy via httpx if desired.
- Add DB verification later via a thin `db.py` helper (SQLAlchemy + MySQL) if needed.
