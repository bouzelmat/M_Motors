# Rapport d'Audit Complet de l'État du Projet M-Motors

Ce document présente un audit exhaustif et technique du projet **M-Motors**. L'objectif est de dresser un état des lieux précis du code existant, d'identifier les écarts par rapport aux spécifications du document `M-Motors_User_Stories_agent_ia_b.md` (architecture hexagonale strict, CQRS, etc.), de lister les lacunes/bugs majeurs, et de proposer une feuille de route claire pour reprendre immédiatement le développement.

---

## 1. Vue d'ensemble du projet

### 📂 Structure Générale du Dépôt
Le projet est séparé en deux dossiers principaux : `backend/` (FastAPI) et `frontend/` (React/Vite).

```
M_Motors/
├── .github/
│   └── workflows/
│       ├── ci.yml            → Pipeline de validation continue
│       └── cd.yml            → Pipeline de déploiement continu
├── backend/
│   ├── alembic/              → Migrations de base de données (Alembic)
│   ├── src/                  → Code source FastAPI
│   └── tests/                → Tests unitaires, intégration et E2E
├── frontend/
│   ├── src/                  → Code source React + Vite
│   └── tests/                → Tests unitaires et E2E
├── docker-compose.yml        → Orchestration locale (Postgres, Backend, Frontend)
└── M-Motors_User_Stories_agent_ia_b.md → Spécifications des User Stories
```

### 🧱 État des Contextes Métier (Backend src/)
L'architecture cible est une architecture hexagonale stricte. L'état actuel des dossiers pour chaque contexte est le suivant :

| Contexte | Couches (`domain`, `application`, `infrastructure`, `api`) | Fichiers Présents / État d'Implémentation |
| :--- | :--- | :--- |
| **`auth/`** | Complètes | **100% Implémenté et fonctionnel** : Entité `User`, VO `Email`/`Role`, Command `RegisterUser`, `JWTService`, `PasswordService` (bcrypt), `SQLAlchemyUserRepository`, endpoints `/register`, `/login`, `/me` et un consommateur asynchrone `SendWelcomeEmailOnUserRegistered`. |
| **`vehicles/`**| Squelette uniquement | **0% Implémenté** : Tous les dossiers existent, mais les fichiers sont des squelettes de 2 lignes contenant uniquement `"""Skeleton module"""`. Aucun code métier, aucun modèle ORM, aucun endpoint réel. |
| **`dossiers/`**| Squelette uniquement | **0% Implémenté** : Structure identique à `vehicles/`. Tous les fichiers existent mais sont vides ou réduits à un squelette docstring (`"""Skeleton module"""`). |
| **`shared/`** | Complètes | **Implémenté et fonctionnel** : Classe de base `Entity`, base `DomainEvent`, exceptions standard (`DomainError`, `NotFoundError`, `ForbiddenError`), moteur et session factory SQLAlchemy (`database.py`), Event Bus in-memory (`event_bus.py`). |

---

## 2. État d'avancement par User Story

L'analyse détaillée montre que seul le **parcours d'authentification (US-301)** et le **socle d'infrastructure de base (US-601)** ont été entamés. Le reste du projet n'est constitué que de squelettes de fichiers.

### 🚗 EPIC 1 — Déploiement de l'offre LLD et services associés
*   **US-101 — Consultation du catalogue LLD** : ❌ **Non fait**
    *   *Fichiers concernés* : `backend/src/vehicles/...`, `frontend/src/vehicles/...`
    *   *Statut* : Fichiers squelettes vides. Pas d'entité `Vehicle`, pas de modèle ORM, pas de Query handler, pas de contrôleur.
*   **US-102 — Affichage des services optionnels LLD** : ❌ **Non fait**
    *   *Statut* : Aucune implémentation du référentiel des services.

### 🔍 EPIC 2 — Recherche et consultation multimodale
*   **US-201 — Recherche de véhicule par mode Achat** : ❌ **Non fait**
    *   *Statut* : Value Object `VehicleSearchCriteria` et filtres de repository inexistants.
*   **US-202 — Recherche de véhicule par mode Location** : ❌ **Non fait**
    *   *Statut* : Non fait.

### 📑 EPIC 3 — Parcours client et dossier 100 % dématérialisé
*   **US-301 — Inscription et création d'espace client** : ⚠️ **Partiellement fait**
    *   *Backend* : ✅ **Fait**. Formulaire validé par Pydantic, hashing cryptographique via passlib, JWT stateless en bearer token, lookup via repository. L'envoi d'e-mail est branché sur l'EventBus de manière asynchrone mais reste un mock (`logger.info`).
    *   *Frontend* : ⚠️ **Partiellement fait**. Les pages `LoginPage.tsx` et `RegisterPage.tsx` ainsi que le store Zustand `useAuthStore` et l'intercepteur de token Axios sont présents et fonctionnels. **Cependant**, la navigation plante à la connexion car `react-router-dom` n'est pas configuré au niveau de l'application et n'est pas déclaré dans les dépendances.
    *   *Tests* : ⚠️ **Partiellement fait**. Les tests unitaires passent, mais tous les tests d'intégration des endpoints d'authentification échouent par manque de configurations (fixtures).
*   **US-301.5 — Personnalisation des services LLD** : ❌ **Non fait**
*   **US-301.6 — Simulation et choix du financement** : ❌ **Non fait**
*   **US-301.7 — Demande de reprise + création du Dossier** : ❌ **Non fait**
*   **US-302 — Upload de pièces justificatives** : ❌ **Non fait**
    *   *Statut* : Pas d'intégration S3, pas de stockage, pas de Dropzone frontend.
*   **US-303 — Suivi de l'avancement du dossier** : ❌ **Non fait**
*   **US-304 — Chiffrement et restriction des accès (RBAC)** : ❌ **Non fait**
*   **US-305 — Purge automatique des données (RGPD)** : ❌ **Non fait**

### ⚙️ EPIC 4 — Gestion dynamique du stock (Back-office)
*   **US-401 — Ajout d'un véhicule au catalogue** : ❌ **Non fait**
*   **US-402 — Basculement d'un véhicule entre stocks** : ❌ **Non fait**

### 📁 EPIC 5 — Instruction et validation des dossiers
*   **US-501 — Visualisation des dossiers en attente** : ❌ **Non fait**
*   **US-502 — Validation ou refus d'un dossier** : ❌ **Non fait**
*   **US-503 — Intégration des données de reprise et de financement** : ❌ **Non fait**

### ☁️ EPIC 6 — Architecture cloud, sécurité et résilience
*   **US-601 — Déploiement automatisé et validation continue (CI/CD)** : ⚠️ **Partiellement fait**
    *   *Docker & docker-compose* : ✅ **Fait et fonctionnels** pour le développement local.
    *   *Healthcheck* : ✅ **Fait**. Le endpoint `GET /health` exécute un `SELECT 1` sur Postgres et renvoie 200 si la base est connectée.
    *   *CI/CD* : ⚠️ **Partiellement fait**. Les workflows GitHub Actions sont écrits, mais le pipeline CI échouera en l'état car `ruff` et `black` ne sont pas déclarés dans `requirements.txt` (donc non installés sur le runner) et la suite de tests d'intégration backend plante.
*   **US-602 — Stratégie de sauvegarde (RPO < 5 min)** : ❌ **Non fait**
*   **US-603 — Script de migration des données historiques** : ❌ **Non fait**
*   **US-604 — Sécurité périmétrique (OWASP)** : ❌ **Non fait** (pas de rate-limiting ni d'audit anti-IDOR).
*   **US-605 — Observabilité (Sentry + CloudWatch)** : ❌ **Non fait**.

---

## 3. Conformité architecturale

### Règle de dépendance hexagonale
La règle fondamentale est respectée dans le code implémenté (`auth/` et `shared/`) :
*   Le domaine n'importe aucun framework externe (pas de SQLAlchemy, FastAPI ou Pydantic).
*   Les value objects (`Email`, `Role`) sont bien structurés comme des dataclasses immuables (`frozen=True`).
*   Les ports (interfaces) sont des `Protocol` Python (`UserRepository.py`).
*   La couche `application/` dépend uniquement des entités et des ports.
*   La couche `infrastructure/` réalise l'implémentation concrète des ports et s'interface avec la base de données.
*   Les endpoints FastAPI dans `api/` injectent proprement les dépendances concrètes via `Depends`.

### ⚠️ Violations et incohérences identifiées
1.  **Schémas Pydantic dans les Routes** : 
    Dans `backend/src/api/rest/auth_routes.py`, les schémas Pydantic (`RegisterRequest`, `RegisterResponse`, `LoginResponse`, `UserResponse`) sont codés directement dans le fichier de routes, alors qu'un dossier dédié aux schémas existe : `src/api/schemas/auth_schemas.py` (qui est actuellement un squelette vide).
2.  **Double Préfixe d'API** :
    Dans `backend/src/api/main.py`, le routeur d'authentification est inclus ainsi :
    ```python
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    ```
    Cependant, dans `auth_routes.py`, le routeur possède déjà son propre préfixe :
    ```python
    router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
    ```
    Cela génère une route effective en `/api/v1/auth/api/v1/auth/register` et `/api/v1/auth/api/v1/auth/login` au lieu du `/api/v1/auth/register` attendu. 
    *Preuve* : Les tests d'intégration d'endpoints appellent directement `"/api/v1/auth/register"` et non la double adresse, mais fonctionnent de manière isolée car ils importent directement le `router` sans passer par l'application complète `main.py` ! C'est une divergence critique entre le comportement de l'API réelle et les tests d'intégration.
3.  **Absence d'implémentation d'UnitOfWork** :
    Bien que requis dans les spécifications pour assurer l'atomicité transactionnelle dans la couche `application`, aucun fichier `unit_of_work.py` n'est implémenté dans `shared/`. Seuls des squelettes de 2 lignes existent dans les sous-dossiers spécifiques `vehicles` et `dossiers`.

---

## 4. Base de données et migrations

### Modèles SQLAlchemy existants
Un seul modèle SQLAlchemy ORM est implémenté dans le projet :
*   `UserModel` (dans `backend/src/auth/infrastructure/orm/user_model.py`) :
    *   Table : `users`
    *   Colonnes : `id` (Uuid, PK), `email` (String, Unique), `hashed_password` (String), `first_name` (String), `last_name` (String), `role` (String), `is_active` (Boolean), `created_at` (DateTime avec fuseau horaire).

Les modèles pour `Vehicle`, `Dossier` et `Document` n'existent pas (squelettes vides).

### État des migrations Alembic
*   Fichier présent : `backend/alembic/versions/20260709_1826_001_create_users_table.py` (Revision ID: `001`).
*   Contenu : Création propre de la table `users` et de l'index sur l'email.
*   Adéquation : En phase avec le modèle `UserModel`.
*   Gaps : Manque de scripts de migration pour la création des tables de véhicules, de services, de dossiers et de justificatifs.

---

## 5. État des Tests

### 🧪 Résultats d'exécution locale

L'exécution de la suite de tests backend remonte le bilan suivant :
*   **15 passés** (tests unitaires sur le domaine).
*   **9 erreurs** (tous les tests d'intégration d'endpoints).

```
=========================== short test summary info ===========================
ERROR tests/integration/test_auth_endpoints.py::test_register_user_success - fixture 'async_client' not found
ERROR tests/integration/test_auth_endpoints.py::test_register_user_duplicate_email - fixture 'async_client' not found
...
======================== 15 passed, 9 errors in 12.33s ========================
```

### 🔬 Inventaire et Analyse des Tests

#### 1. Tests Unitaires Backend (Fonctionnels)
*   `test_email.py` (7 tests) : Valide le format des adresses e-mail, l'égalité structurelle, et l'immutabilité du Value Object `Email`.
*   `test_user.py` (7 tests) : Valide la création de l'entité `User`, l'assignation par défaut de la date de création, le rôle `ADMIN` ou `CLIENT`, la méthode `get_full_name()`, et l'égalité d'entités basée uniquement sur l'UUID.
*   `test_health.py` (1 test) : Valide l'endpoint de liveness `/health` en bypassant la vraie base de données via un mock d'AsyncSession (`DummySession`).

#### 2. Tests d'Intégration Backend (En erreur)
*   `test_auth_endpoints.py` : Écrit mais **complètement inutilisable**. Tous les tests demandent les fixtures `async_client` (de type `AsyncClient` de HTTPX) et `db_session` (de type `AsyncSession` de SQLAlchemy). **Aucun fichier `conftest.py` n'est configuré dans le projet pour fournir ces fixtures.**
*   `test_dossier_repository.py`, `test_unit_of_work.py`, `test_vehicle_repository.py` : Sont des squelettes vides de 2 lignes.

#### 3. Tests E2E (Playwright)
*   Backend et Frontend : Les fichiers de tests E2E Playwright (`test_dossier_creation_flow.py`, `test_vehicle_search.py`) ne contiennent aucun code et ne sont pas configurés.

#### 4. Tests Frontend (Vitest)
*   `App.test.tsx` (1 test) : Passe avec succès. Valide uniquement que le titre du composant `App` s'affiche bien.
*   Aucun autre test n'est écrit pour les formulaires ou le store Zustand.

---

## 6. Infrastructure et déploiement

### Docker et docker-compose
Les fichiers d'infrastructure locale sont propres :
*   `docker-compose.yml` : Définit un service Postgres 16 avec un healthcheck (`pg_isready`), le service `backend` exposant le port 8000 et le service `frontend` exposant le port 3000 (servi via un port 80 mappé).
*   `backend/Dockerfile` : Base `python:3.12-slim`, installation de `build-essential`, copie de la source, création d'un utilisateur non-root `appuser`, et lancement du serveur via Uvicorn.
*   `frontend/Dockerfile` : Build multi-étape. Étape 1 : Build Node 20 qui compile le site. Étape 2 : Nginx Alpine léger qui sert les fichiers statiques de l'application via `nginx.conf`.

### CI/CD (GitHub Actions)
*   `ci.yml` : S'exécute sur push/PR sur `main` et `develop`. Lance Ruff, Black, Pytest et Vitest.
    *   **Problème majeur** : Ruff et Black ne sont pas listés dans le `requirements.txt` du backend. Le pipeline CI va crasher à l'étape de peluchage/linting car ces outils ne seront pas installés sur la machine virtuelle de GitHub.
*   `cd.yml` : Se déclenche sur push vers `main`. Gère le build des images Docker et supporte le déploiement sur Render (via Webhook) ou sur AWS ECS Fargate (avec build, tag ECR et mise à jour du service).

### Intégration S3 et variables d'environnement
L'intégration S3 pour stocker les pièces justificatives des dossiers clients (EPIC 3) est **inexistante**. Aucun paramètre boto3, aucun secret AWS ou nom de bucket n'est configuré dans `config.py` ou dans le fichier `.env` local.

---

## 7. Événements et bus d'événements

### Pattern in-memory
L'EventBus est implémenté sous forme d'un bus in-memory synchrone asynchrone (`event_bus.py` dans `shared`). Il permet d'enregistrer des handlers par type d'événement (qui héritent de `DomainEvent`).
*   **Événement Défini** : `UserRegistered` contenant `user_id`, `email`, `first_name` et `last_name`.
*   **Événement Publié** : Publié dans le handler `RegisterUserCommandHandler` après une insertion DB réussie.
*   **Consommateur** : `SendWelcomeEmailOnUserRegistered` est instancié au démarrage, s'abonne à `UserRegistered` et logge l'action à des fins de simulation.
*   **Divergence** : Aucun autre événement métier (`VehicleAdded`, `DossierSubmitted`, `DossierValidated`, etc.) n'est codé. Leurs fichiers sont des squelettes.

---

## 8. Points bloquants et lacunes majeures

Voici les failles critiques et dysfonctionnements du code qui empêchent le projet de tourner correctement ou d'être étendu :

1.  **Défaut de Fixtures de Tests d'Intégration** : 
    L'absence d'un `conftest.py` empêche l'exécution de tous les tests d'intégration d'API. Un développeur arrivant sur le projet ne peut pas valider ses modifications.
2.  **Dépendance de Navigation Frontend Absente** :
    Le package `react-router-dom` est importé dans les fichiers de pages frontend (`LoginPage.tsx`, etc.), mais il est **absent** du fichier `package.json`. L'installation de base `npm install` ne récupère pas cette dépendance essentielle, provoquant des erreurs de compilation/build immédiates si ces pages sont importées.
3.  **Absence d'un Routeur Applicatif au Niveau du Frontend** :
    `main.tsx` charge directement le composant `App.tsx` qui affiche une page d'atterrissage statique. Il n'y a aucun composant de type `<BrowserRouter>` ou de configuration de routes (`/login`, `/register`, `/dashboard`) pour lier les pages d'authentification existantes.
4.  **Erreur de Montage du Routeur (Double Préfixe) Backend** :
    FastAPI expose les routes sur `/api/v1/auth/api/v1/auth/register` à cause de la redondance des préfixes configurés dans `main.py` et `auth_routes.py`.
5.  **Typo dans la Configuration Environnementale** :
    Le fichier `.env` du backend déclare `ENVONMENT=development` au lieu de `ENVIRONMENT`.
6.  **Dépendances de CI Non Déclarées** :
    `ruff` et `black` sont configurés dans les étapes de validation GitHub Actions, mais ne font pas partie du `requirements.txt`.
7.  **Squelettes sans Logique pour la LLD et les Dossiers** :
    Les contextes `vehicles` et `dossiers` n'ont aucune logique métier implémentée (0%). Les checklists des EPICs 1, 2, 3, 4 et 5 sont vierges.

---

## 9. Recommandations et Plan de reprise

Pour débloquer et accélérer le développement, voici l'ordre des tâches préconisé :

### Étape 1 : Résolution des Bugs de Socle (Priorité Haute)
1.  **Créer le fichier `conftest.py`** :
    Mettre en place les fixtures de test pytest (`async_client` et `db_session`) dans `backend/tests/conftest.py` pour corriger les 9 tests d'intégration en échec.
2.  **Corriger le double préfixe dans `main.py`** :
    Supprimer le préfixe additionnel de FastAPI lors de l'inclusion d'un routeur déjà préfixé, pour avoir des URLs propres (ex : `/api/v1/auth/register`).
3.  **Mettre à jour les dépendances frontend** :
    Installer et ajouter `react-router-dom` dans le `package.json` du frontend :
    ```bash
    npm install react-router-dom
    ```
4.  **Installer le Routeur Frontend** :
    Modifier `main.tsx` et `App.tsx` pour y intégrer un routeur de base (`react-router-dom`) et brancher les composants `LoginPage`, `RegisterPage` et `DossiersPage` (Dashboard).
5.  **Mettre à jour les dépendances du pipeline CI** :
    Ajouter `ruff` et `black` dans le fichier `backend/requirements.txt`.

### Étape 2 : Implémentation du Catalogue (EPIC 1 & 2)
1.  Développer l'entité `Vehicle` pure (`backend/src/vehicles/domain/entities/vehicle.py`) avec la règle métier `is_available()`.
2.  Créer le modèle ORM `VehicleModel`, mapper `VehicleMapper` et implémenter `SQLAlchemyVehicleRepository`.
3.  Créer la migration Alembic pour générer la table `vehicles` et son association avec les options.
4.  Mettre en place l'endpoint `GET /api/v1/vehicles` filtrable par type de catalogue (`mode=rental` ou `mode=sale`).

### Étape 3 : Implémentation des Dossiers Clients (EPIC 3)
1.  Implémenter l'agrégat `Dossier` avec son cycle de vie (statuts `INITIALIZED` à `VALIDATED`/`REJECTED`/`PURGED`).
2.  Mettre en place la configuration S3 privée et coder le service d'upload via presigned URLs PUT (US-302).
3.  Développer les vérifications d'autorisation objet (anti-IDOR) (US-304).
4.  Écrire le script cron de purge RGPD (US-305).
