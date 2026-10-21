# M-Motors

Guide de démarrage de l'application sous Windows avec PowerShell. Le démarrage complet avec Docker Compose est le mode recommandé : PostgreSQL, l'API FastAPI et le frontend servi par Nginx tournent dans des conteneurs.

## Prérequis

- Docker Desktop installé et démarré
- Node.js et Python uniquement si vous choisissez le mode de développement local décrit plus bas

Toutes les commandes Docker ci-dessous sont à exécuter depuis la racine du dépôt.

## Démarrer l'application avec Docker

Construire les images et démarrer l'application avec PostgreSQL, l'API, le frontend et S3Mock (stockage S3 local) :

```powershell
docker compose up --build -d
```

Au premier démarrage, le backend applique automatiquement les migrations Alembic avant de lancer l'API. PostgreSQL et S3Mock conservent leurs données dans les volumes Docker `postgres_data` et `s3mock_data`. S3Mock crée automatiquement les buckets de démonstration `m-motors-documents` et `m-motors-photos`.

Vérifier que les services sont démarrés :

```powershell
docker compose ps
```

Adresses locales :

- Application : http://localhost:3000
- Catalogue : http://localhost:3000/catalogue
- Connexion : http://localhost:3000/login
- Inscription : http://localhost:3000/register
- API : http://localhost:8000
- Documentation Swagger : http://localhost:8000/docs
- Santé de l'API et de la base : http://localhost:8000/health
- Stockage S3 local : http://localhost:9000

S3Mock et ses identifiants factices sont réservés au développement local ; ils ne vérifient pas les signatures et ne doivent jamais servir en production. Aucun compte Amazon ni identifiant AWS n'est nécessaire pour déposer des pièces en local. Le backend parle à S3Mock sur le réseau Docker ; les URLs présignées utilisent `localhost:9000` et le proxy Nginx applique CORS pour les frontends locaux sur les ports 3000 et 5173. Le stockage de production reste AWS S3.

La route `/health` doit répondre avec `{"status":"ok","database":"reachable"}`. L'interface Docker est un build de production servi par Nginx : elle n'utilise pas le rechargement à chaud de Vite.

Dans `backend/.env`, `DATABASE_URL` utilise `localhost` pour le lancement du backend directement sous Windows. Docker Compose surcharge cette variable dans le conteneur backend avec l'hôte `db`, qui correspond au service PostgreSQL du réseau Docker. Il n'est donc pas nécessaire de remplacer `localhost` dans le fichier `.env` pour lancer le mode Docker.

En mode Docker, le frontend appelle l'API sur son origine (`http://localhost:3000`) avec des chemins comme `/api/v1/...`. Nginx relaie ces requêtes vers le backend en conservant le chemin. Ce proxy same-origin évite les problèmes CORS pour les appels du frontend ; il ne change pas les règles CORS pour les accès directs à l'API depuis une autre origine.

Le fichier `backend/.env` contient de la configuration locale et peut contenir des secrets : ne le commitez jamais. Il est exclu de Git par le `.gitignore` à la racine du dépôt.

## Créer le compte administrateur

Une fois les conteneurs démarrés, exécuter le seed depuis le conteneur backend :

```powershell
docker compose exec backend python scripts/seed_admin.py
```

Le script est idempotent : le relancer ne crée pas de doublon. Par défaut, il utilise `admin@example.com` et `Admin123!Secure`, sauf si les variables `SEED_ADMIN_EMAIL` et `SEED_ADMIN_PASSWORD` sont définies. Ces valeurs sont réservées au développement et ne doivent pas être utilisées en production ( pour connaitre les identifiants de production il faut consulter la Copie examen )

## Remplir les catalogues de démonstration

Une base neuve ne contient aucun véhicule : les deux pages de catalogue sont donc vides jusqu'à l'ajout de véhicules. Pour insérer des exemples dans les modes vente et location, exécuter :

```powershell
docker compose exec backend python scripts/seed_demo_vehicles.py
```

Le script ajoute deux véhicules en vente et deux en location. Il conserve les autres données et ignore ses propres véhicules s'ils existent déjà ; vous pouvez le relancer sans supprimer ni dupliquer les véhicules du catalogue.

En mode développement local, depuis la racine du dépôt :

```powershell
Set-Location .\backend
.\venv\Scripts\python.exe scripts/seed_demo_vehicles.py
```

## Arrêter et redémarrer

Arrêter les conteneurs sans supprimer les données :

```powershell
docker compose down
```

Les données PostgreSQL restent dans `postgres_data`. Pour redémarrer plus tard :

```powershell
docker compose up -d
```

**Attention :** `docker compose down -v` supprime aussi le volume PostgreSQL et donc les données locales.

## Consulter les journaux

```powershell
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

Pour reconstruire après une modification d'une dépendance ou d'un Dockerfile :

```powershell
docker compose up --build -d
```

## Développement avec le rechargement à chaud

Utilisez ce mode si vous souhaitez lancer le backend avec Uvicorn et le frontend avec Vite directement depuis Windows. Ne démarrez pas simultanément les conteneurs backend/frontend, car ils utilisent les mêmes ports (`8000` et `3000`).

### 1. Démarrer PostgreSQL et le stockage local

Depuis la racine du dépôt :

```powershell
docker compose down
docker compose up -d db s3mock s3-proxy
```

### 2. Démarrer le backend localement

Le terminal doit être placé dans `backend` pour que la configuration locale soit chargée :

```powershell
Set-Location .\backend
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Le fichier `backend/.env` doit utiliser `localhost` pour PostgreSQL lorsque le backend tourne hors de Docker :

```text
DATABASE_URL=postgresql+asyncpg://m_motors:m_motors@localhost:5432/m_motors
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=local
AWS_ENDPOINT_URL=http://localhost:9090
AWS_PUBLIC_ENDPOINT_URL=http://localhost:9000
S3_DOCUMENTS_BUCKET_NAME=m-motors-documents
```

Si la base vient d'être créée ou ne contient pas encore les tables, appliquez les migrations depuis `backend` :

```powershell
.\venv\Scripts\python.exe -m alembic upgrade head
```

### 3. Démarrer le frontend localement

Dans un autre terminal PowerShell :

```powershell
Set-Location .\frontend
npm ci
npm run dev
```

Vite est disponible sur http://localhost:5173. Pour revenir au mode Docker complet, arrêtez les processus locaux (`Ctrl+C`), revenez à la racine, puis lancez `docker compose up --build -d`.

## Dépannage rapide

Vérifier l'état des services :

```powershell
docker compose ps
```

Consulter les erreurs de démarrage du backend :

```powershell
docker compose logs --tail=100 backend
```

Si un port est déjà utilisé, arrêtez le processus local ou le conteneur qui l'occupe avant de relancer l'application. Pour vérifier la connexion du backend à PostgreSQL, ouvrez http://localhost:8000/health.