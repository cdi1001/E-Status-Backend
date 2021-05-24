GITHUB_PAGES_BRANCH=gh-pages
BASEDIR=$(CURDIR)
OUTPUTDIR=$(BASEDIR)/output

.PHONY: available
available:
	pip install -r requirements/base.txt
	python available.py

.PHONY: generate
generate:
	pip install -r requirements/base.txt
	python performancepage.py

.PHONY: generate_dev
generate_dev:
	python performancepage.py --dev

.PHONY: watch
watch:
	python watch.py

.PHONY: publish
publish:
	pip install -r requirements/base.txt
	python performancepage.py
	ghp-import -m "Generate Performance page" -b $(GITHUB_PAGES_BRANCH) $(OUTPUTDIR)
	git push origin $(GITHUB_PAGES_BRANCH)

.PHONY: publish_travis
publish_travis:
	pip install -r requirements/base.txt
	python performancepage.py
	ghp-import -m "Generate Performance page" -b $(GITHUB_PAGES_BRANCH) $(OUTPUTDIR)

.PHONY: test
test:
	pass
