# M_Motors

Le projet concerne une application réalisée dans le cadre d'une validation d'un examen de fin d'étude.

## Démarrage local recommandé

Le scénario conseillé pour le développement est le suivant:

- backend lancé en local depuis `backend/venv`
- PostgreSQL lancé dans Docker
- frontend lancé en local ou via Docker selon le besoin

### 1. Démarrer PostgreSQL

Depuis la racine du projet:

```powershell
Set-Location 'C:\Users\User1\AppData\Local\Temp\M_Motors'
docker compose up -d db
```

Vérification:

```powershell
docker compose ps
```

Le service `db` doit être démarré et healthy.

### 2. Démarrer le backend en local

Depuis le dossier backend:

```powershell
Set-Location 'C:\Users\User1\AppData\Local\Temp\M_Motors\backend'
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Test de santé:

```powershell
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8000/health'
```

Réponse attendue:

```json
{"status":"ok","database":"reachable"}
```

### 3. Démarrer le frontend en local

Depuis le dossier frontend:

```powershell
Set-Location 'C:\Users\User1\AppData\Local\Temp\M_Motors\frontend'
npm install
npm run dev
```

Le frontend Vite démarre généralement sur `http://localhost:5173`.

## Alternative: démarrage complet avec Docker

Si tu veux tout lancer en conteneurs:

```powershell
Set-Location 'C:\Users\User1\AppData\Local\Temp\M_Motors'
docker compose up -d --build
```

Services exposés:

- PostgreSQL: `localhost:5432`
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
