# TriMaint — Commandes Makefile

.PHONY: up down build logs shell-backend migrate revision rollback status

## Démarrer l'application
up:
	docker compose up -d

## Démarrer avec rebuild forcé
build:
	docker compose up --build -d

## Arrêter l'application
down:
	docker compose down

## Arrêter et supprimer les volumes (ATTENTION : efface la BDD)
down-v:
	docker compose down -v

## Voir les logs en temps réel
logs:
	docker compose logs -f

## Logs backend seulement
logs-backend:
	docker compose logs -f backend

## Shell dans le conteneur backend
shell-backend:
	docker compose exec backend bash

## Appliquer toutes les migrations en attente
migrate:
	docker compose exec backend alembic upgrade head

## Créer une nouvelle migration (usage: make revision MSG="description")
revision:
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

## Revenir à la migration précédente
rollback:
	docker compose exec backend alembic downgrade -1

## Revenir à l'état vide (ATTENTION : supprime toutes les tables)
rollback-all:
	docker compose exec backend alembic downgrade base

## Voir l'historique des migrations
history:
	docker compose exec backend alembic history --verbose

## Voir la migration courante
status:
	docker compose exec backend alembic current
