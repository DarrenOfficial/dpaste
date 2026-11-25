#
# Makefile that handles all the static file compilation and
# adds some helper tools for daily development.
#

SHELL=/bin/bash -eu -o pipefail

define N # newline


endef

.PHONY: test
test: ## Run Django tests
	docker compose run --rm app pytest dpaste/

.PHONY: code-cleanup
code-cleanup: ## Black and isort the Python codebase
	autoflake --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables \
          --in-place --exclude "**/migrations/*,dpaste/settings/local.py" -r dpaste
	isort dpaste
	black --exclude='/(migrations)/' dpaste

.PHONY: css
css: ## Compile SCSS files
	npx sass --no-source-map --style=compressed --quiet-deps --silence-deprecation=import,global-builtin,color-functions client/scss/dpaste.scss:dpaste/static/dpaste.css

.PHONY: css-watch
css-watch: ## Compile SCSS files (watch stylesheets and recompile when they change)
	npx sass --watch client/scss/dpaste.scss:dpaste/static/dpaste.css

.PHONY: js
js: ## Compile JS files
	npx terser client/js/dpaste.js --compress drop_console=true,ecma=2015 --mangle toplevel --output dpaste/static/dpaste.js

.PHONY: release-docker
release-docker:
	set -ex
	rm -f .coverage
	docker build --build-arg BUILD_EXTRAS=production -t darrenofficial/dpaste:latest .
	@echo -e "\n\n💫 All fine. Now do: docker push darrenofficial/dpaste:latest"

.PHONY: release-pypi
release-pypi:
	set -ex
	rm -f .coverage
	docker compose build
	docker compose run --rm app pytest dpaste/
	rm -rf ./node_modules
	npm ci
	make css
	make js
	python -m build
	@echo -e "\n\n💫 All fine. Now do: twine upload dist/*"

.PHONY: help
help:
	@echo -e "Available make commands:"
	@echo -e ""
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sort | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

.DEFAULT_GOAL := help
