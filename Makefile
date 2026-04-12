.PHONY: dev infra api web migrate test clean

# Start all infrastructure (Postgres, Gitea, MinIO)
infra:
	docker compose -f infra/docker-compose.yml up -d

infra-down:
	docker compose -f infra/docker-compose.yml down

# Run API server
api:
	cd apps/api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run frontend dev server
web:
	cd apps/web && npm run dev

# Run both API + frontend
dev: infra
	$(MAKE) -j2 api web

# Database migrations
migrate:
	cd apps/api && alembic upgrade head

migrate-new:
	cd apps/api && alembic revision --autogenerate -m "$(msg)"

# Tests
test:
	cd apps/api && pytest
	cd apps/web && npm test

# Clean docker volumes
clean:
	docker compose -f infra/docker-compose.yml down -v
