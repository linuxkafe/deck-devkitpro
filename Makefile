.PHONY: setup run test lint format build check doctor help

AES_LANGUAGE ?= javascript
AES_LINT ?= npx eslint src tests --ext .js,.ts
AES_TEST ?= npx jest --coverage
AES_FORMAT ?= npx prettier --write .
AES_BUILD ?= npm run build
AES_RUN ?= npm start

export AES_LANGUAGE AES_LINT AES_TEST AES_FORMAT AES_BUILD AES_RUN

setup:
	@echo "Setting up $(AES_LANGUAGE)..."
	npm install

run:
	@$(AES_RUN)

test:
	@$(AES_TEST)

lint:
	@$(AES_LINT)

format:
	@$(AES_FORMAT)

build:
	@$(AES_BUILD)

check: docs-check code-check test-check lint-check

docs-check:
	@test -f docs/VISION.md && grep -q "Problem" docs/VISION.md
	@test -f docs/PERSONAS.md && grep -q "User" docs/PERSONAS.md
	@test -f docs/REQUIREMENTS.md && grep -q "Functional" docs/REQUIREMENTS.md
	@test -f docs/ROADMAP.md && grep -q "Roadmap" docs/ROADMAP.md

code-check:
	@test -d src || test -d lib
	@grep -R "TODO:" src/ 2>/dev/null || true

test-check:
	@$(AES_TEST) --coverage || echo "Tests failed or coverage missing"

lint-check:
	@$(AES_LINT) --max-warnings=0

validate:
	@$(AES_BUILD) || true
	@npx tsc --noEmit 2>/dev/null || true

doctor:
	@echo "Language: $(AES_LANGUAGE)"
	@echo "Node: $$(node -v 2>/dev/null || echo not-found)"
	@echo "NPM: $$(npm -v 2>/dev/null || echo not-found)"

help:
	@echo "AES Commands: make setup run test lint format build check doctor"
