# TriMaint — GMAO Triselec

Système de gestion de maintenance industrielle (CMMS) pour les usines de tri Triselec.

## Stack technique

| Composant | Technologie |
|-----------|------------|
| Backend   | FastAPI (Python 3.11) |
| Frontend  | React + Vite + TypeScript + Tailwind CSS |
| Base de données | PostgreSQL 16 |
| Auth      | JWT (PyJWT + bcrypt) |
| Reverse proxy | Nginx |
| Conteneurisation | Docker + Docker Compose |

## Démarrage rapide

### Prérequis

- Docker ≥ 24
- Docker Compose ≥ 2.x

### 1. Cloner le projet

```bash
git clone <repo-url>
cd trimaint
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
```

**Les variables `POSTGRES_PASSWORD` et `SECRET_KEY` sont obligatoires.** Le serveur refusera de démarrer si elles sont absentes ou trop faibles.

```bash
# Générer des secrets sécurisés
openssl rand -hex 16  # → POSTGRES_PASSWORD
openssl rand -hex 32  # → SECRET_KEY
```

Éditez `.env` et collez les valeurs générées.

### 3. Lancer l'application

```bash
docker compose up --build -d
```

L'application est disponible sur **http://localhost** (port 80 par défaut).

### Premier démarrage

Au premier lancement, un compte administrateur est créé automatiquement :

| Champ | Valeur |
|-------|--------|
| Utilisateur | `admin` |
| Mot de passe | Affiché **une seule fois** dans les logs du backend |

Récupérez le mot de passe temporaire dans les logs :

```bash
docker compose logs backend | grep "Mot de passe temporaire"
```

> ⚠️ **Changez ce mot de passe immédiatement après la première connexion.**

Vous pouvez aussi prédéfinir le mot de passe via la variable `INITIAL_ADMIN_PASSWORD` dans `.env`.

## Variables d'environnement

| Variable | Obligatoire ? | Défaut | Description |
|----------|:---:|--------|-------------|
| `POSTGRES_DB` | | `trimaint` | Nom de la base de données |
| `POSTGRES_USER` | | `trimaint` | Utilisateur PostgreSQL |
| `POSTGRES_PASSWORD` | ✅ | *(aucun)* | Mot de passe PostgreSQL |
| `SECRET_KEY` | ✅ | *(aucun)* | Clé secrète JWT (min. 32 caractères, `openssl rand -hex 32`) |
| `CORS_ORIGINS` | | `localhost` | Origines autorisées (séparées par virgule) |
| `ENABLE_API_DOCS` | | `false` | Activer Swagger/ReDoc (`true`/`false`) |
| `PORT` | | `80` | Port exposé par le frontend |
| `INITIAL_ADMIN_PASSWORD` | | *(aléatoire)* | Mot de passe admin initial (si non fourni, généré automatiquement) |

## Déploiement sur Coolify

1. Créer un nouveau projet dans Coolify
2. Choisir **Docker Compose** comme type de déploiement
3. Pointer vers ce dépôt Git
4. Définir les variables d'environnement dans l'interface Coolify :
   - `POSTGRES_PASSWORD` → mot de passe sécurisé (`openssl rand -hex 16`)
   - `SECRET_KEY` → clé aléatoire (`openssl rand -hex 32`)
   - `CORS_ORIGINS` → votre domaine (ex. `https://trimaint.example.com`)
5. Cliquer sur **Deploy**

## Architecture des services Docker

```
                    ┌──────────────┐
        Port 80     │   Frontend   │  nginx
   ──────────────▶  │  (React SPA) │
                    └──────┬───────┘
                           │ proxy /api/*
                    ┌──────▼───────┐
                    │   Backend    │  FastAPI + uvicorn
                    │  Port 8000   │
                    └──────┬───────┘
                           │ SQLAlchemy
                    ┌──────▼───────┐
                    │  PostgreSQL  │  Port 5432 (interne)
                    │   Port 5432  │
                    └──────────────┘
```

## Fonctionnalités

- 🔐 **Authentification** — JWT, rôles admin / manager / technicien, rate-limiting
- 🏭 **Machines** — CRUD complet + génération QR code
- ⚠️ **Pannes** — Enregistrement avec criticité, causes, solution, export CSV
- 🔧 **Interventions** — Suivi, photos avant/après, validation manager, technicien forcé
- 📦 **Pièces détachées** — Stock, emplacement, fournisseur
- 🔍 **Recherche globale** — Recherche unifiée machines / pannes / interventions
- 📊 **Dashboard** — Statistiques temps réel, top pannes, état des machines
- 📎 **Upload fichiers** — Images et PDF, validation par magic bytes, sanitisation Pillow
- 🔔 **Notifications** — Alertes automatiques pannes critiques et maintenance préventive
- 🔒 **Sécurité** — RBAC par endpoint, CORS strict, mot de passe admin aléatoire

## API Documentation

Swagger UI activable via `ENABLE_API_DOCS=true` : **http://localhost/api/docs**

## Commandes utiles

```bash
# Voir les logs
docker compose logs -f

# Logs d'un service spécifique
docker compose logs -f backend

# Arrêter l'application
docker compose down

# Arrêter et supprimer les données (ATTENTION : irréversible)
docker compose down -v

# Rebuild après modification du code
docker compose up --build -d
```

## Structure du projet

```
trimaint/
├── backend/
│   ├── app/
│   │   ├── api/          # Routes FastAPI (RBAC par rôle)
│   │   ├── core/         # Config, sécurité, notifications, activity log
│   │   ├── db/           # Session SQLAlchemy
│   │   ├── models/       # Modèles ORM
│   │   └── schemas/      # Schémas Pydantic (EmailStr, validation)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   └── services/
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
└── README.md
```
