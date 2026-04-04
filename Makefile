HOST_UID := $(shell id -u)
HOST_GID := $(shell id -g)

.PHONY: up build-runtime validate-runtime

build-runtime:
	docker compose build toolkit

up: build-runtime
	HOST_UID=$(HOST_UID) HOST_GID=$(HOST_GID) docker compose run --rm toolkit

validate-runtime: build-runtime
	HOST_UID=$(HOST_UID) HOST_GID=$(HOST_GID) docker compose run --rm toolkit validate
