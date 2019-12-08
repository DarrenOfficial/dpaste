#
# Makefile that handles all the static file compilation and
# adds some helper tools for daily development.
#

SHELL=/bin/bash -eu -o pipefail

define N # newline


endef

.PHONY: test
test: ## Run Django tests
	docker-compose run --rm app pytest dpaste/

.PHONY: code-cleanup
code-cleanup: ## Black and isort the Python codebase
	autoflake --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables \
          --exclude "**/migrations/*,dpaste/settings/local.py" -r dpaste
	isort -rc dpaste
	black --line-length=80 --exclude='/(migrations)/' dpaste

.PHONY: docs
docs: ## Compile the documentation
	docker-compose run --rm app sphinx-build docs docs/_build/html

.PHONY: watch-docs
docs-watch: ## Compile the documentation and watch for changes
	docker-compose run --rm app sphinx-autobuild docs docs/_build/html

.PHONY: css
css: ## Compile SCSS files
	npx sass --no-source-map --style=compressed client/scss/dpaste.scss:dpaste/static/dpaste.css

.PHONY: css-watch
css-watch: ## Compile JS files
	npx sass --watch client/scss/dpaste.scss:dpaste/static/dpaste.css

.PHONY: js
js: ## Compile JS files
	npx uglifyjs --compress="drop_console=true,ecma=6" --mangle="toplevel" --output=dpaste/static/dpaste.js client/js/dpaste.js

.PHONY: release-docker
release-docker:
	set -ex
	docker-compose run --rm app pytest dpaste/
	docker build --build-arg BUILD_EXTRAS=production -t barttc/dpaste:latest .
	@echo -e "\n\n💫 All fine. Now do: docker push barttc/dpaste:latest"

.PHONY: release-pypi
release-pypi:
	set -ex
	docker-compose run --rm app pytest dpaste/
	rm -rf ./node_modules
	npm ci
	make css
	make js
	python setup.py sdist && python setup.py bdist_wheel --universal
	@echo -e "\n\n💫 All fine. Now do: twine upload dist/* --sign"

.PHONY: help
help:
	@echo -e "Available make commands:"
	@echo -e ""
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sort | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

.DEFAULT_GOAL := start
