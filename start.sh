#!/bin/bash

cd /home/runner/workspace/backend

echo "Migration de la base de données..."

# Détecte si la DB a déjà les tables mais pas encore alembic_version (pré-Alembic)
NEEDS_STAMP=$(uv run python - <<'PYEOF'
import os, sys
try:
    import psycopg2
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        print("no"); sys.exit(0)
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name='alembic_version')")
    has_alembic = cur.fetchone()[0]
    cur.execute("SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name='users')")
    has_tables = cur.fetchone()[0]
    conn.close()
    print("yes" if (has_tables and not has_alembic) else "no")
except Exception as e:
    print("no", file=sys.stderr)
    print("no")
PYEOF
)

if [ "$NEEDS_STAMP" = "yes" ]; then
    echo "Base pré-Alembic détectée, estampillage révision 0001..."
    uv run alembic stamp 0001
fi

uv run alembic upgrade head
echo "Migrations terminées."

# Backend
uv run python -m uvicorn app.main:app --host localhost --port 8000 --reload &
echo "Backend démarré"

# Frontend
cd /home/runner/workspace/frontend
npm run dev
