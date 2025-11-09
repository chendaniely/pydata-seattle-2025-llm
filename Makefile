.PHONY: preview
preview:
	cd website && quarto preview

.PHONY: render
render:
	cd website && quarto render

.PHONY: setup-python
setup-python:
	uv venv .venv
	source .venv/bin/activate && uv pip install -r requirements.txt

.PHONY: setup-quarto
setup-quarto:
	cd website && \
		quarto add --no-prompt coatless-quarto/embedio && \
		quarto add --no-prompt gadenbuie/countdown/quarto && \
		quarto add --no-prompt quarto-ext/shinylive

.PHONY: setup
setup:
	make setup-python
	make setup-quarto

.PHONY: clean
clean:
	rm -rf .venv venv

.PHONY: publish
publish:
	quarto publish gh-pages website
