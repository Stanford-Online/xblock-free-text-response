## Localization targets

WORKDIR := $(module_root)

translations_extract: ## extract strings to be translated, outputting .po files
	# Extract Python and Django template strings
	mkdir -p $(WORKDIR)/translations/en/LC_MESSAGES/
	tox -e translations_extract
	# cat $(WORKDIR)/translations/en/LC_MESSAGES/django-partial.po | \
	# 	grep -v 'Plural-Forms: nplurals' > $(WORKDIR)/translations/en/LC_MESSAGES/text.po
	# rm -f $(WORKDIR)/translations/en/LC_MESSAGES/django-partial.po

translations_compile: ## compile translation files, outputting .mo files for each supported language
	tox -e translations_compile

translations_detect_changed: ## Determines if the source translation files are up-to-date, otherwise exit with a non-zero code.
	tox -e translations_detect_changed

translations_pull: ## pull translations from Transifex
	tox -e translations_pull
	make translations_compile

translations_push: translations_extract ## push source translation files (.po) to Transifex
	tox -e translations_push

translations_dummy: ## generate dummy translation (.po) files
	tox -e translations_dummy

translations_build_dummy: translations_extract translations_dummy translations_compile ## generate and compile dummy translation files

translations_validate: translations_build_dummy translations_detect_changed ## validate translations
