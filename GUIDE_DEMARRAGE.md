# Guide de demarrage de M-Motors

Ce fichier explique, pas a pas, comment lancer l'application en local.
Il est volontairement plus detaille que le README pour aider un debutant.

## 1. Architecture a retenir

Le projet utilise le scenario suivant:

- le backend FastAPI tourne en local sur Windows
- PostgreSQL tourne dans Docker
- le frontend peut tourner en local ou dans Docker

Le bon environnement Python pour le backend est:

- `backend/venv`

Ne pas utiliser l'ancien environnement virtuel a la racine du projet.

## 2. Pre-requis

Avant de commencer, il faut avoir:

- Docker Desktop installe et demarre
- Python installe localement si tu veux recreer le venv
- Node.js installe si tu veux lancer le frontend en local

## 3. Lancer la base de donnees PostgreSQL

La base de donnees est fournie par Docker Compose.

### Commande

```powershell
Set-Location 'C:\Users\User1\AppData\Local\Temp\M_Motors'
docker compose up -d db
```

### Explication

- `Set-Location` place le terminal a la racine du projet
- `docker compose up -d db` demarre uniquement le service PostgreSQL
- le port expose est `5432`

### Verification

```powershell
docker compose ps
```

Tu dois voir le service `db` en etat `healthy` ou `running`.

### Arret de la base

```powershell
docker compose stop db
```

Si tu veux supprimer le conteneur:

```powershell
docker compose down
```

## 4. Lancer le backend FastAPI en local

Le backend doit etre lance depuis le dossier `backend` avec le bon venv.

### Commande

```powershell
Set-Location 'C:\Users\User1\AppData\Local\Temp\M_Motors\backend'
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

### Explication

- on se place dans `backend` pour que le fichier `.env` soit lu correctement
- on utilise `backend/venv` car il contient les dependances a jour
- `uvicorn` demarre l'API sur `http://127.0.0.1:8000`

### Ce que le backend doit trouver

Le fichier `backend/.env` doit contenir une URL de ce type:

```text
DATABASE_URL=postgresql+asyncpg://m_motors:m_motors@localhost:5432/m_motors
```

Cette URL signifie:

- utilisateur PostgreSQL: `m_motors`
- mot de passe PostgreSQL: `m_motors`
- base de donnees: `m_motors`
- port local: `5432`

### Verification du backend

Une fois le serveur demarre, teste la route de sante:

```powershell
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8000/health'
```

La reponse attendue est:

```json
{"status":"ok","database":"reachable"}
```

### Arret du backend

Dans le terminal ou Uvicorn tourne, faire `Ctrl + C`.

## 5. Si le backend ne demarre pas

Si tu vois une erreur sur les dependances ou sur la connexion PostgreSQL, verifie dans cet ordre:

1. Docker est bien demarre.
2. Le conteneur `db` est bien lance.
3. Tu utilises bien `backend/venv` et pas le venv racine.
4. Le fichier `backend/.env` contient la bonne URL `DATABASE_URL`.

Tu peux aussi tester la connexion direct depuis Python:

```powershell
Set-Location 'C:\Users\User1\AppData\Local\Temp\M_Motors\backend'
.\venv\Scripts\python.exe -c "import asyncio; from sqlalchemy import text; from src.shared.infrastructure.database import get_engine; async def main():\n    engine = get_engine()\n    async with engine.connect() as conn:\n        result = await conn.execute(text('SELECT 1'))\n        print(result.scalar_one())\n    await engine.dispose()\nasyncio.run(main())"
```

Si la commande affiche `1`, la connexion database fonctionne.

## 6. Lancer le frontend en local

Le frontend se trouve dans le dossier `frontend`.

### Premiere installation

```powershell
Set-Location 'C:\Users\User1\AppData\Local\Temp\M_Motors\frontend'
npm install
```

### Demarrage

```powershell
npm run dev
```

### Explication

- `npm install` telecharge les dependances du frontend
- `npm run dev` lance Vite en mode developpement

### Adresse du frontend

En general, le frontend est disponible sur:

- `http://localhost:5173`

## 7. Lancer toute l'application avec Docker

Si tu veux tout demarrer avec Docker Compose, sans lancer le backend en local:

### Commande

```powershell
Set-Location 'C:\Users\User1\AppData\Local\Temp\M_Motors'
docker compose up -d --build
```

### Explication

- `--build` reconstruit les images si le code a change
- le service `db` expose PostgreSQL sur `5432`
- le service `backend` expose l'API sur `8000`
- le service `frontend` expose l'interface sur `3000`

### Verification

```powershell
docker compose ps
```

Puis teste:

```powershell
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8000/health'
```

## 8. Commandes utiles de maintenance

### Voir les logs Docker

```powershell
docker compose logs -f db
docker compose logs -f backend
docker compose logs -f frontend
```

### Redemarrer un service

```powershell
docker compose restart db
docker compose restart backend
docker compose restart frontend
```

### Arreter tout le stack

```powershell
docker compose down
```

## 9. Resume rapide

Ordre le plus simple pour lancer le projet en local:

1. Demarrer Docker Desktop
2. Lancer PostgreSQL avec `docker compose up -d db`
3. Lancer le backend avec `backend/venv`
4. Tester `http://127.0.0.1:8000/health`
5. Lancer le frontend avec `npm run dev`
