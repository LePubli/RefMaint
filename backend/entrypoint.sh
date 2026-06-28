#!/bin/bash
set -e

echo "=== TriMaint Backend ==="
echo "Attente de PostgreSQL..."

# Attendre que PostgreSQL soit prêt
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(os.environ['DATABASE_URL'])
    sys.exit(0)
except Exception as e:
    print(f'  PostgreSQL non disponible: {e}')
    sys.exit(1)
"; do
    sleep 2
done

echo "PostgreSQL prêt."

echo "Exécution des migrations Alembic..."
alembic upgrade head
echo "Migrations terminées."

echo "Démarrage du serveur FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
