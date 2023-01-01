.PHONY: help start stop test run rebuild

DEV_COMPOSE=docker-compose --file docker-compose.yml

.SILENT:

include .env
export

start:
	$(DEV_COMPOSE) up -d --build --remove-orphans

stop: 
	$(DEV_COMPOSE) stop

test:
	$(DEV_COMPOSE) exec -T ssc2ce /bin/bash -c 'pytest'

run:
	$(DEV_COMPOSE) run --rm ssc2ce /bin/bash -c '$(cmd)'

rebuild:
	$(DEV_COMPOSE) up -d --no-deps --build ssc2ce