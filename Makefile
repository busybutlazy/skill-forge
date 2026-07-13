HOST_UID := $(shell id -u)
HOST_GID := $(shell id -g)

.PHONY: up pull build-local validate-runtime dev

pull:
	docker compose pull forge

up: pull
	HOST_UID=$(HOST_UID) HOST_GID=$(HOST_GID) docker compose run --rm forge

validate-runtime: pull
	HOST_UID=$(HOST_UID) HOST_GID=$(HOST_GID) docker compose run --rm forge validate

# build the runtime image locally (for development / before pushing)
build-local:
	docker build -t ghcr.io/busybutlazy/skill-forge:local .

dev:
	docker compose build forge-dev
	docker compose run --rm forge-dev
