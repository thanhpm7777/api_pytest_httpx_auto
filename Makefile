.PHONY: venv install test smoke schemathesis contract perf \
        allure open-allure clean-allure \
        docker-build docker-test docker-smoke docker-schemathesis docker-perf docker-shell docker-allure

# ===== Python local =====
venv:
	python -m venv .venv && . .venv/Scripts/activate && python -m pip install --upgrade pip

install:
	python -m pip install -r requirements.txt

# Full suite (trừ các suite đặc biệt)
test:
	pytest -n auto --alluredir=reports/allure-results

# Smoke nhanh
smoke:
	pytest -m smoke -n auto --alluredir=reports/allure-results

schemathesis:
	pytest -m schemathesis -k test_openapi --maxfail=1 --alluredir=reports/allure-results

contract:
	pytest -m contract -n auto --alluredir=reports/allure-results

perf:
	locust -f perf/locustfile.py --headless -u 50 -r 10 -t 2m --csv=reports/locust

# ===== Allure =====
allure:
	allure generate reports/allure-results -c -o reports/allure

open-allure:
	allure serve reports/allure-results

clean-allure:
	python -c "import shutil; shutil.rmtree('reports/allure', ignore_errors=True); shutil.rmtree('reports/allure-results', ignore_errors=True)"

# ===== Docker =====
docker-build:
	# Nếu muốn BuildKit: đặt biến env trước khi build trong PowerShell:
	#   $env:DOCKER_BUILDKIT="1"
	docker build -t api-tests:latest .

docker-test:
	docker run --rm -v "$(CURDIR)":/app -w /app api-tests:latest \
		pytest -n auto --alluredir=/app/reports/allure-results

docker-smoke:
	docker run --rm -v "$(CURDIR)":/app -w /app api-tests:latest \
		pytest -m smoke -n auto --alluredir=/app/reports/allure-results

docker-schemathesis:
	docker run --rm -v "$(CURDIR)":/app -w /app api-tests:latest \
		pytest -m schemathesis -k test_openapi --maxfail=1 --alluredir=/app/reports/allure-results

docker-perf:
	docker run --rm -v "$(CURDIR)":/app -w /app api-tests:latest \
		locust -f perf/locustfile.py --headless -u 50 -r 10 -t 2m --csv=/app/reports/locust

docker-shell:
	docker run --rm -it -v "$(CURDIR)":/app -w /app api-tests:latest powershell

docker-allure:
	allure generate reports/allure-results -c -o reports/allure
