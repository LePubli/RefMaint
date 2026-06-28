# TriMaint — GMAO Triselec

## Project Overview

TriMaint is an industrial maintenance management system (CMMS/GMAO) built for Triselec sorting plants. It centralizes industrial equipment data, breakdowns, maintenance interventions, spare parts, and technical documentation.

## Architecture

- **Backend**: FastAPI (Python 3.11) on `localhost:8000`
- **Frontend**: React + Vite + TypeScript + Tailwind CSS on `0.0.0.0:5000`
- **Database**: PostgreSQL (Replit managed)
- **Auth**: JWT (using python-jose + bcrypt directly)

## How to Run

The project starts via `start.sh` which launches both services:
```bash
bash start.sh
```

Or via the Replit workflow "Start application".

## Default Login

- Username: `admin`
- Password: `admin123`

## Key Pages

- `/` — Dashboard with statistics
- `/machines` — Machine management (CRUD + QR codes)
- `/pannes` — Breakdown management with CSV export
- `/interventions` — Intervention tracking with manager validation
- `/pieces` — Spare parts inventory
- `/recherche` — Global search across all records

## API

FastAPI docs available at: `http://localhost:8000/docs`

## Notes

- File uploads stored in `backend/data/uploads/`
- QR codes auto-generated for each machine on creation
- Roles: admin, manager, technicien
- bcrypt is used directly (not via passlib) due to bcrypt v4+ incompatibility with passlib's __about__ module

## User Preferences

- Industrial dark UI theme (gray-900 / orange-500 accent)
- French language interface
