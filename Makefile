.PHONY: dev test lint docker-build docker-run

dev:
	py -m src.bot_app

test:
	py -m pytest -q

docker-build:
	docker build -t gate-bot:latest .

docker-run:
	docker run --rm -it --env-file .env gate-bot:latest