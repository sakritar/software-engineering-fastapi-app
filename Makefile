DC = docker compose
EXEC = docker exec -it
DOCKER_COMPOSE_FILE = docker-compose.yml
ENV_FILE = --env-file .env
APP_CONTAINER = app
EXEC_APP = ${EXEC} ${APP_CONTAINER}
POETRY_RUN = ${EXEC_APP} poetry run

.PHONY: migrate
migrate:
	${POETRY_RUN} alembic upgrade head

.PHONY: shell
shell:
	${EXEC_APP} /bin/ash

.PHONY: up
up:
	${DC} -f ${DOCKER_COMPOSE_FILE} ${ENV_FILE} up -d

.PHONY: down
down:
	${DC} -f ${DOCKER_COMPOSE_FILE} ${ENV_FILE} down

.PHONY: rebuild
rebuild:
	${DC} -f ${DOCKER_COMPOSE_FILE} ${ENV_FILE} up --build --force-recreate -d

.PHONY: lf
lf:
	find . -type f -exec dos2unix {} \;
