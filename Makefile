LANGFUSE_DIR ?= ../langfuse # change depending on your local environment

COMPOSE := docker compose
LANGFUSE_COMPOSE := $(COMPOSE) --project-directory $(LANGFUSE_DIR) -f $(LANGFUSE_DIR)/docker-compose.yml

.PHONY: up down restart app-up app-down langfuse-up langfuse-down clean

up: langfuse-up app-up

down: app-down langfuse-down

restart: down up

app-up:
	$(COMPOSE) up -d --wait

app-down:
	$(COMPOSE) down

langfuse-up:
	@test -f $(LANGFUSE_DIR)/docker-compose.yml || { echo "Langfuse not found at $(LANGFUSE_DIR) (set LANGFUSE_DIR=...)"; exit 1; }
	$(LANGFUSE_COMPOSE) up -d

langfuse-down:
	$(LANGFUSE_COMPOSE) down

clean:
	$(COMPOSE) down -v
	$(LANGFUSE_COMPOSE) down
