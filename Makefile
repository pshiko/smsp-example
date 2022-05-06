docker-test: build-docker
	docker run --rm smsp-example:develop poetry run pytest --durations=9 -vv

docker-run: build-docker
	docker run --rm -it smsp-example:develop /bin/bash

build-docker:
	docker build . -t smsp-example:develop

install-poetry-shell:
	poetry install && poetry run maturin develop --release
