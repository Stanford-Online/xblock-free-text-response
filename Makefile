#!/usr/bin/make -f
module_root := freetextresponse
css_files := $(patsubst %.less, %.css, $(wildcard ./$(module_root)/public/*.less))
html_files := $(wildcard $(module_root)/templates/*.html)
js_files := $(wildcard $(module_root)/public/*.js)
py_files := $(wildcard $(module_root)/**/*.py)
files_with_translations := $(js_files) $(html_files) $(py_files)
translation_root := $(module_root)/translations
po_files := $(wildcard $(translation_root)/*/LC_MESSAGES/*.po)
ifneq ($(strip $(language)),)
	po_files := $(po_files) $(translation_root)/$(language)/LC_MESSAGES/text.po
endif
ifeq ($(strip $(po_files)),)
	po_files = $(translation_root)/en/LC_MESSAGES/text.po
endif
mo_files := $(patsubst %.po,%.mo,$(po_files))

.PHONY: help
help:  ## This.
	@perl -ne 'print if /^[a-zA-Z_-]+:.*## .*$$/' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: runserver
runserver: build_docker  ## Run server inside XBlock Workbench container
	$(docker_run) $(_NAME)

.PHONY: clean
clean:  ## Remove build artifacts
	tox -e clean
	rm -rf reports/cover
	rm -rf .tox/
	rm -rf *.egg-info/
	rm -rf .eggs/
	rm -rf package-lock.json
	rm -rf node_modules/
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete

.PHONY: quality
quality: requirements  # Run all quality checks
	tox -e csslint,eslint,pycodestyle,pylint

.PHONY: requirements
requirements: requirements_js requirements_py  ## Install all required packages

.PHONY: requirements_py
requirements_py:  # Install required python packages
	pip install tox==3.7.0

.PHONY: requirements_js
requirements_js:  # Install required javascript packages
	npm install

.PHONY: static
static: requirements_js $(css_files)  ## Compile the less->css
$(module_root)/public/%.css: $(module_root)/public/%.less
	@echo "$< -> $@"
	node_modules/less/bin/lessc $< $@

.PHONY: test
test: requirements  ## Run all quality checks and unit tests
	tox -p all

# extract
%.po: $(files_with_translations)
	mkdir -p $(@D)
	./manage.py makemessages -l "$(patsubst $(translation_root)/%/LC_MESSAGES,%,$(@D))"
	mv "$(patsubst %/text.po,%/django.po,$(@))" "$(@)"

# compile
%.mo: %.po
	msgfmt -o "$(@)" "$(<)"

.PHONY: translations
translations:  ## Update translation files
	make $(mo_files)
	@echo
	@echo 'Translations up-to-date.'
	@echo "You can add a new language like this:"
	@echo '	make $(@) language=fr'
	@echo 'where `fr` is the language code.'
	@echo

include *.mk

_NAME=free-text-response:latest
_VOLUME=-v '$(PWD):/root/xblock'
_PORT=
runserver: _PORT = -p 8000:8000
docker_test: _VOLUME = -v '$(PWD)/reports:/root/xblock/reports'
docker_run=docker run $(_PORT) $(_VOLUME) --rm -it
docker_make=$(docker_run) --entrypoint make $(_NAME)
docker_make_args=language=$(language) -C /root/xblock
docker_make_more=$(docker_make) $(docker_make_args)

.PHONY: build_docker
build_docker:
	docker build -t $(_NAME) .
.PHONY: docker_static docker_test docker_translations
define run-in-docker
$(docker_make_more) $(patsubst docker_%, %, $@)
endef
docker_shell:
	$(docker_run) --entrypoint /bin/bash $(_NAME)
docker_static: ; make build_docker; $(run-in-docker)  ## Compile static assets in docker container
docker_translations: ; make build_docker; $(run-in-docker)  ## Update translation files in docker container
docker_test: ; make build_docker; $(run-in-docker)  ## Run tests in docker container
