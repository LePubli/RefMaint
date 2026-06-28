# TriMaint — GMAO Triselec

Système de gestion de maintenance industrielle (CMMS) pour les usines de tri Triselec.

## Stack technique

| Composant | Technologie |
|-----------|------------|
| Backend   | FastAPI (Python 3.11) |
| Frontend  | React + Vite + TypeScript + Tailwind CSS |
| Base de données | PostgreSQL 16 |
| Auth      | JWT (python-jose + bcrypt) |
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
# Éditer .env et changer les mots de passe
```

### 3. Lancer l'application

```bash
docker compose up --build -d
```

L'application est disponible sur **http://localhost** (port 80 par défaut).

### Identifiants par défaut

| Champ | Valeur |
|-------|--------|
| Utilisateur | `admin` |
| Mot de passe | `admin123` |

> ⚠️ Changez le mot de passe admin dès la première connexion en production.

## Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `POSTGRES_DB` | `trimaint` | Nom de la base de données |
| `POSTGRES_USER` | `trimaint` | Utilisateur PostgreSQL |
| `POSTGRES_PASSWORD` | *(requis)* | Mot de passe PostgreSQL |
| `SECRET_KEY` | *(requis)* | Clé secrète JWT (min. 32 caractères) |
| `PORT` | `80` | Port exposé par le frontend |

## Déploiement sur Coolify

1. Créer un nouveau projet dans Coolify
2. Choisir **Docker Compose** comme type de déploiement
3. Pointer vers ce dépôt Git
4. Définir les variables d'environnement dans l'interface Coolify :
   - `POSTGRES_PASSWORD` → mot de passe sécurisé
   - `SECRET_KEY` → clé aléatoire de 64 caractères
5. Cliquer sur **Deploy**

### Générer une SECRET_KEY sécurisée

```bash
openssl rand -hex 32
```

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

- 🔐 **Authentification** — JWT, rôles admin / manager / technicien
- 🏭 **Machines** — CRUD complet + génération QR code
- ⚠️ **Pannes** — Enregistrement avec criticité, causes, solution, export CSV
- 🔧 **Interventions** — Suivi, photos avant/après, validation manager
- 📦 **Pièces détachées** — Stock, emplacement, fournisseur
- 🔍 **Recherche globale** — Recherche unifiée machines / pannes / interventions
- 📊 **Dashboard** — Statistiques temps réel, top pannes, état des machines
- 📎 **Upload fichiers** — Images et PDF stockés localement dans `/data/uploads`

## API Documentation

Swagger UI disponible sur : **http://localhost/api/docs**  
ReDoc disponible sur : **http://localhost/api/redoc**

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
│   │   ├── api/          # Routes FastAPI
│   │   ├── core/         # Config, sécurité
│   │   ├── db/           # Session SQLAlchemy
│   │   ├── models/       # Modèles ORM
│   │   └── schemas/      # Schémas Pydantic
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
