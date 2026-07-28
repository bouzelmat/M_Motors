# User Stories — M-Motors
### Backlog technique enrichi pour exécution par agent IA + gestion via GitHub Projects

---

## 🧭 Comment utiliser ce document

Chaque US ci-dessous est rédigée pour être **collée telle quelle comme corps d'issue GitHub**. Le titre de section (`US-XXX — ...`) devient le titre de l'issue.

**Configuration GitHub Projects recommandée :**
- Champ **Priority** (single select) : Critique / Haute / Moyenne
- Champ **Story Points** (number)
- Champ **Epic** (single select, 1 par EPIC) — ou utiliser les **Milestones** GitHub, un par EPIC
- Champ **Status** : Todo / In Progress / In Review / Done
- **Labels** : `type:backend`, `type:frontend`, `type:infra`, `type:security`, `epic:1`…`epic:6`

Chaque US contient une checklist **« Tâches pour l'agent IA »** — laisse-la telle quelle dans l'issue : ton agent (Claude Code) peut cocher chaque ligne au fur et à mesure, ce qui te donne un suivi d'avancement natif dans GitHub.

Les critères d'acceptation restent au format **Given/When/Then** (cohérent avec Playwright pour les tests E2E).

---

## 🧩 Modèle de domaine de référence — Architecture hexagonale stricte (Ports & Adapters)

À copier dans un fichier `docs/domain-model.md` du repo — référence unique pour l'agent IA sur tous les tickets. **Séparation stricte** : le domaine ne connaît aucun framework (ni SQLAlchemy, ni FastAPI, ni Pydantic).

### Arborescence, identique pour chaque bounded context (`auth/`, `véhicules/`, `dossiers/`)

```
<context>/
├── domain/
│   ├── entities/        → classes métier pures (aucun import SQLAlchemy/FastAPI)
│   ├── value_objects/   → objets immuables (Email, FinancingPlan, TradeIn, VehicleSearchCriteria...)
│   └── ports/           → interfaces (typing.Protocol) : repositories, services externes
├── application/
│   ├── commands/        → Command handlers (write, CQRS) — dépendent uniquement des ports
│   └── queries/         → Query handlers (read, CQRS) — dépendent uniquement des ports
├── infrastructure/
│   ├── orm/              → modèles SQLAlchemy (Base, Column, relationship...)
│   ├── mappers/           → to_domain() / to_orm() entre entité pure et modèle ORM
│   ├── repositories/      → implémentations concrètes des ports (Adapters)
│   └── adapters/          → adapters vers d'autres contextes ou services externes (S3, email...)
└── api/
    └── routers/           → endpoints FastAPI, injectent les implémentations via `Depends`
```

**Règle de dépendance stricte** : `domain/` ne dépend de rien d'autre dans le projet. `application/` dépend uniquement de `domain/` (entités, value objects, ports). `infrastructure/` implémente les ports définis dans `domain/` et peut dépendre de tout (SQLAlchemy, boto3, bibliothèques externes). `api/` orchestre en injectant les implémentations concrètes dans les handlers.

**Ports en Python** : `typing.Protocol` (typage structurel) plutôt qu'une hiérarchie `ABC` — une classe qui expose les bonnes méthodes satisfait le port sans héritage explicite à déclarer.

### `auth/`
- `domain/entities/User.py` : `id`, `email` (VO `Email`), `hashed_password`, `first_name`, `last_name`, `role`, `is_active`, `created_at`
- `domain/ports/UserRepository.py` : `save(user)`, `find_by_email(email) -> User | None`, `find_by_id(id) -> User | None`
- `infrastructure/orm/UserModel.py` · `infrastructure/mappers/UserMapper.py` · `infrastructure/repositories/SQLAlchemyUserRepository.py`
- ⚠️ **Scope assumé** : le hashing de mot de passe (bcrypt/argon2) et la génération JWT restent des services techniques injectés directement dans les Command handlers, sans port dédié — ce sont des mécanismes de sécurité, pas des règles métier. Dis-le-moi si tu veux les faire passer aussi par un port (`PasswordHasherPort`, `TokenServicePort`) pour aller au bout de la logique.
- ⚠️ **Rôles** : `CLIENT`, `ADMIN` (seuls rôles définis dans le schéma d'architecture). Les US-501/502/503 parlent de « conseiller », distinct de l'« administrateur » des US-401/402 — pour le MVP, `ADMIN` couvre les deux ; extensible en `ADVISOR` sans casser l'existant.

### `véhicules/`
- `domain/entities/Vehicle.py` : `id`, `brand`, `model`, `mileage`, `fuel_type`, `year`, `photos[]`, `sale_price`, `monthly_rent`, `catalog_type` (`SALE`|`RENTAL`), `status` (`AVAILABLE`|`RESERVED`|`SOLD`|`RENTED`) + méthodes métier `is_available()`, `switch_to_rental()`, `switch_to_sale()`, `mark_as_rented()`, `mark_as_sold()` — les transitions de statut sont des méthodes de l'entité, jamais un `vehicle.status = "X"` écrit depuis un handler
- `domain/entities/Service.py` : `id`, `name`, `monthly_cost`, `category` (`INSURANCE`|`ASSISTANCE`|`MAINTENANCE`|`INSPECTION`)
- `domain/value_objects/VehicleSearchCriteria.py` : `brand`, `max_price`, `max_mileage`, `fuel_type`, `mode`, `max_monthly_rent`
- `domain/ports/VehicleRepository.py` : `save(vehicle)`, `find_by_id(id)`, `find_by_criteria(criteria) -> list[Vehicle]`
- `domain/ports/DossierExistencePort.py` : `has_active_dossier_for_vehicle(vehicle_id) -> bool` — permet à `véhicules/` d'interroger `dossiers/` sans en dépendre directement
- `infrastructure/orm/VehicleModel.py`, `ServiceModel.py`, `VehicleServiceModel.py` (association) · `infrastructure/mappers/VehicleMapper.py` · `infrastructure/repositories/SQLAlchemyVehicleRepository.py` · `infrastructure/adapters/DossierExistenceAdapter.py` (implémente le port ci-dessus)

### `dossiers/`
- `domain/entities/Dossier.py` (Aggregate Root) : `id`, `client_id`, `vehicle_id`, `type`, `status`, `selected_services[]`, `financing_plan` (VO), `trade_in` (VO, optionnel), `created_at`, `decision_comment`, `rejected_at` + méthodes métier `submit()`, `approve(comment)`, `reject(reason)`, `request_documents(types)`, `is_owned_by(client_id)`, `is_rejected_since(days) -> bool` — chaque transition lève une `DomainError` si elle est invalide (ex. approuver un dossier déjà `REJECTED`)
- `domain/entities/Document.py` : `id`, `dossier_id`, `type`, `s3_key`, `status`
- `domain/value_objects/FinancingPlan.py` : `down_payment`, `duration_months`, `monthly_payment`
- `domain/value_objects/TradeIn.py` : `registration`, `mileage`, `brand`, `model`, `estimated_value`
- `domain/ports/DossierReadRepository.py` : `find_pending(sort_by) -> list[Dossier]`, `find_by_id(id) -> Dossier | None`
- `domain/ports/DossierWriteRepository.py` : `save(dossier)`, `find_by_id(id) -> Dossier | None` (séparé du read repository — cohérent avec le CQRS déjà retenu dans l'architecture)
- `domain/ports/DocumentRepository.py` : `save(document)`, `find_by_id(id)`, `find_by_dossier(dossier_id) -> list[Document]`
- `infrastructure/orm/DossierModel.py`, `DocumentModel.py` · `infrastructure/mappers/DossierMapper.py`, `DocumentMapper.py` · `infrastructure/repositories/SQLAlchemyDossierReadRepository.py`, `SQLAlchemyDossierWriteRepository.py`, `SQLAlchemyDocumentRepository.py`
- **Cycle de vie du statut** : `INITIALIZED → DOCUMENTS_PENDING → SUBMITTED → IN_REVIEW → (VALIDATED | REJECTED) → [si REJECTED + 30j] → PURGED`

### `shared/` (Kernel)
- `domain/entity.py` : classe `Entity` de base (égalité par `id`)
- `application/unit_of_work.py` : interface `UnitOfWork` (+ implémentation SQLAlchemy) — garantit qu'une commande sauvegarde ses agrégats de façon atomique
- `application/event_bus.py` : interface `EventBus` (+ implémentation in-memory pour le MVP, migration prévue vers Outbox Pattern + SQS)
- `domain/exceptions.py` : `DomainError`, `NotFoundError`, `ForbiddenError`
- `infrastructure/db.py` : moteur + session factory SQLAlchemy — **jamais importé dans `domain/` ou `application/`**, uniquement dans `infrastructure/`

### Événements (inchangé)
Définis dans le schéma d'architecture : `VehicleAdded`, `VehicleRented`, `DossierSubmitted`, `DossierValidated`, `DossierRejected`.
Extensions proposées, même convention (Entité + participe passé) : `VehicleListedForSale`, `DossierInitialized`, `DocumentsRequested`, `DossierPurged`.

**Stack rappel (cf. Choix définitifs)** : FastAPI async + Pydantic, SQLAlchemy + Alembic, PostgreSQL, JWT/OAuth2, S3 (URLs pré-signées), React 19 + TS + MUI + Zustand + Axios/React Query, tests pytest+httpx (back) / Vitest+RTL (front), Ruff+Black, Sentry+CloudWatch.

---

## EPIC 1 — Déploiement de l'offre LLD et services associés

### US-101 — Consultation du catalogue LLD

**Labels :** `epic:1`, `type:backend`, `type:frontend` · **Priorité :** Haute · **Story Points :** 3

**User Story**
En tant que client, je veux consulter la liste des véhicules disponibles en LLD afin de comparer les offres avant de m'engager.

**Contexte technique** — Bounded context `véhicules/`, côté **Query** (CQRS read model).

**Critères d'acceptation**
- Given un client sur la page d'accueil, When il sélectionne le mode « Location », Then il voit la liste des véhicules LLD avec photo, modèle, prix mensuel et services inclus.
- Given un véhicule LLD, When le client clique dessus, Then il voit le détail (assurance, assistance, entretien, contrôle technique inclus ou en option).
- Given aucun véhicule disponible, When la liste est vide, Then un message « Aucun véhicule disponible pour le moment » s'affiche.

**Contrat API**
```
GET /api/v1/vehicles?mode=rental
GET /api/v1/vehicles/{id}
```
Réponse liste : `VehicleListItemDTO { id, brand, model, monthly_rent, photo_url, included_services: string[] }`
Réponse détail : ajoute `services: [{id, name, monthly_cost, included: bool}]`

**Tâches pour l'agent IA**
- [ ] Backend : entité métier `Vehicle` pure dans `véhicules/domain/entities/Vehicle.py` (aucun `Column`, aucun héritage `Base`) + méthode `is_available()` portant la règle métier ci-dessous
- [ ] Backend : modèle `VehicleModel` SQLAlchemy dans `véhicules/infrastructure/orm/` + migration Alembic (`catalog_type`, `status`)
- [ ] Backend : `VehicleMapper.to_domain()` / `to_orm()` dans `véhicules/infrastructure/mappers/`
- [ ] Backend : interface `VehicleRepository` (Protocol) dans `véhicules/domain/ports/` — `save()`, `find_by_id()`, `find_by_criteria()`
- [ ] Backend : implémentation `SQLAlchemyVehicleRepository` dans `véhicules/infrastructure/repositories/`
- [ ] Backend : **règle métier** — les listes publiques ne renvoient jamais un véhicule `RESERVED`, `SOLD` ou `RENTED` ; le repository applique `status = AVAILABLE` par défaut (sauf appel back-office explicite, cf. US-501), en s'appuyant sur `Vehicle.is_available()`
- [ ] Backend : Query handler `GetRentalCatalogQuery` (`véhicules/application/queries/`) — dépend uniquement de l'interface `VehicleRepository`, jamais de SQLAlchemy directement
- [ ] Backend : endpoint `GET /vehicles` avec filtre `mode`, gestion liste vide (200 + `[]`, pas de 404)
- [ ] Backend : endpoint `GET /vehicles/{id}` avec jointure `VehicleService`
- [ ] Frontend : hook `useVehiclesQuery(mode)` (React Query)
- [ ] Frontend : composant `VehicleCard` (MUI) + état vide `EmptyCatalogMessage`
- [ ] Tests : tests unitaires sur l'entité `Vehicle` (méthode `is_available()`, sans DB) ; tests d'intégration pytest sur le repository avec base de test ; pytest sur les 2 endpoints (cas nominal + liste vide + vérification qu'un véhicule `SOLD` n'apparaît jamais) ; test Vitest sur `VehicleCard`
- [ ] 🧪 Playwright suggéré : `catalog.spec.ts` → sélection mode Location → assertion carte véhicule visible

**Définition of Done**
- [ ] Swagger à jour (FastAPI auto-doc)
- [ ] Couverture tests ≥ critères du projet
- [ ] Déployé en staging (Render)

**Dépendances :** aucune (fondation du catalogue)

---

### US-102 — Affichage des services optionnels LLD

**Labels :** `epic:1`, `type:backend`, `type:frontend` · **Priorité :** Haute · **Story Points :** 2

**User Story**
En tant que client, je veux voir les services disponibles en option pour chaque véhicule LLD afin d'estimer le coût total de mon abonnement.

**Critères d'acceptation**
- Given la fiche d'un véhicule LLD, When les services optionnels sont disponibles, Then chacun est affiché avec son intitulé et son coût mensuel additionnel.
- Given un service inclus, When il est affiché, Then il est labellisé « Inclus » sans coût additionnel.

**Tâches pour l'agent IA**
- [ ] Backend : seed de données `Service` (assurance tous risques, assistance dépannage, entretien/SAV, contrôle technique)
- [ ] Backend : s'assurer que `GET /vehicles/{id}` renvoie `included: true/false` par service (déjà couvert par US-101, vérifier ici en priorité)
- [ ] Frontend : composant `ServiceOptionRow` avec badge MUI « Inclus » vs prix
- [ ] Tests : Vitest sur l'affichage conditionnel du badge

**Dépendances :** US-101

---

## EPIC 2 — Recherche et consultation multimodale des véhicules

### US-201 — Recherche de véhicule par mode Achat

**Labels :** `epic:2`, `type:backend`, `type:frontend` · **Priorité :** Critique · **Story Points :** 5

**User Story**
En tant que client, je veux filtrer les véhicules d'occasion par marque, budget, kilométrage et motorisation afin de trouver rapidement le véhicule adapté.

**Critères d'acceptation**
- Given le mode « Achat », When le client applique des filtres (ex. budget max 15 000 €, essence), Then la liste se met à jour en temps réel.
- Given aucun résultat, When les filtres sont trop restrictifs, Then un message « Aucun véhicule ne correspond à vos critères » s'affiche avec suggestion d'ajuster les filtres.
- Given un véhicule Achat, When le client clique dessus, Then il accède à la fiche détaillée (photos, historique, garantie, prix).

**Contrat API**
```
GET /api/v1/vehicles?mode=sale&brand=&max_price=&max_mileage=&fuel_type=
```

**Tâches pour l'agent IA**
- [ ] Backend : value object `VehicleSearchCriteria` dans `véhicules/domain/value_objects/` (`brand`, `max_price`, `max_mileage`, `fuel_type`, `mode`) — objet unique de critères plutôt que des paramètres épars, réutilisé tel quel par US-202
- [ ] Backend : méthode `find_by_criteria(criteria)` sur l'interface `VehicleRepository` (définie en US-101) ; l'implémentation `SQLAlchemyVehicleRepository` construit le `WHERE` conditionnel **dans l'infrastructure uniquement** — le Query handler ne connaît que l'interface, jamais SQLAlchemy directement (éviter le SQL injection en gardant l'ORM, jamais de concat de string)
- [ ] Backend : le filtre `status = AVAILABLE` de US-101 s'applique aussi ici par défaut (même règle métier sur `Vehicle.is_available()`, pas de duplication de logique)
- [ ] Backend : indexation DB sur `brand`, `fuel_type`, `sale_price` (perf recherche)
- [ ] Frontend : store Zustand `useVehicleFilterStore` (état des filtres)
- [ ] Frontend : hook `useVehiclesQuery` avec `queryKey` incluant les filtres (cache React Query par combinaison de filtres)
- [ ] Frontend : debounce (300ms) sur les inputs numériques pour limiter les appels API
- [ ] Frontend : composant `EmptyResultsMessage` avec CTA « Modifier mes filtres »
- [ ] Tests : tests d'intégration pytest sur `SQLAlchemyVehicleRepository.find_by_criteria()` avec base de test, combinaisons de filtres (nominal, valeurs nulles, combinaisons vides)
- [ ] 🧪 Playwright suggéré : `search-sale.spec.ts` → filtrer par budget → vérifier liste filtrée + cas résultat vide

**Dépendances :** US-101 (réutilise l'entité `Vehicle` et l'interface `VehicleRepository`)

---

### US-202 — Recherche de véhicule par mode Location

**Labels :** `epic:2`, `type:backend`, `type:frontend` · **Priorité :** Critique · **Story Points :** 5

**User Story**
En tant que client, je veux filtrer les véhicules LLD par type, durée de contrat et budget mensuel afin d'identifier les offres adaptées.

**Critères d'acceptation**
- Given le mode « Location », When le client filtre par budget mensuel (≤ 400 €/mois), Then seuls les véhicules concernés s'affichent.
- Given les deux modes disponibles, When le client passe de « Achat » à « Location », Then l'interface se met à jour sans rechargement de page.

**Tâches pour l'agent IA**
- [ ] Backend : ajouter `max_monthly_rent` au DTO `VehicleSearchCriteria` de US-201 (pas un paramètre séparé) ; le repository applique `max_price` si `mode = SALE`, `max_monthly_rent` si `mode = RENTAL`
- [ ] Frontend : toggle Achat/Location piloté par le store Zustand global (pas de reload, changement de `queryKey` React Query uniquement)
- [ ] Frontend : synchroniser le mode dans l'URL (`?mode=rental`) pour permettre le partage de lien (nice-to-have, non bloquant)
- [ ] Tests : Vitest sur le switch de mode (vérifier absence de remount complet de page)

**Dépendances :** US-101, US-201 (partage la logique de filtrage)

---

## EPIC 3 — Parcours client et dossier 100 % dématérialisé

> Contexte transverse important : les US 301.5 → 301.7 forment un **tunnel de souscription multi-étapes**. Recommandation d'implémentation : garder l'état du tunnel (services choisis, plan de financement, reprise) **côté frontend** (store Zustand dédié `useSubscriptionTunnelStore`), et ne créer l'agrégat `Dossier` en base qu'à la validation finale (US-301.7). Cela évite de gérer des « paniers » serveur éphémères et simplifie le back-end.

### US-301 — Inscription et création d'espace client

**Labels :** `epic:3`, `type:backend`, `type:frontend`, `type:security` · **Priorité :** Critique · **Story Points :** 3

**User Story**
En tant que visiteur intéressé par un véhicule, je veux créer un compte client afin d'accéder à l'espace de dépôt de dossier.

**Contexte technique** — Bounded context `auth/`.

**Critères d'acceptation**
- Given un visiteur non connecté cliquant sur « Je suis intéressé », When il remplit le formulaire (email, mot de passe, nom, prénom), Then son compte est créé et il reçoit un e-mail de confirmation.
- Given un email déjà enregistré, When le visiteur tente de s'inscrire, Then un message d'erreur explicite s'affiche.
- Given un compte créé, When l'utilisateur se connecte, Then il accède à son tableau de bord personnel.

**Contrat API**
```
POST /api/v1/auth/register  { email, password, first_name, last_name }  → 201 | 409 (email déjà utilisé)
POST /api/v1/auth/login     { email, password }                          → 200 { access_token, refresh_token }
GET  /api/v1/auth/me        (Bearer token)                               → 200 { id, email, role, ... }
```

**Tâches pour l'agent IA**
- [ ] Backend : entité métier `User` pure dans `auth/domain/entities/User.py` (aucun `Column`, aucun héritage `Base`)
- [ ] Backend : modèle `UserModel` SQLAlchemy dans `auth/infrastructure/orm/` + migration Alembic, contrainte unique sur `email`
- [ ] Backend : `UserMapper.to_domain()` / `to_orm()` dans `auth/infrastructure/mappers/`
- [ ] Backend : interface `UserRepository` (Protocol) dans `auth/domain/ports/` — `save()`, `find_by_email()`, `find_by_id()` ; implémentation `SQLAlchemyUserRepository` dans `auth/infrastructure/repositories/`
- [ ] Backend : hashing mot de passe (passlib + bcrypt/argon2) — service technique injecté dans le Command handler, jamais de mot de passe en clair en base ni dans les logs
- [ ] Backend : Command handler `RegisterUserCommand` dépendant uniquement de `UserRepository` — endpoint `register` avec validation Pydantic (format email, complexité mot de passe minimale)
- [ ] Backend : endpoint `login` OAuth2 password flow, génération JWT (`access_token` courte durée + `refresh_token`)
- [ ] Backend : dépendance FastAPI `get_current_user` (décodage JWT + lookup via `UserRepository`)
- [ ] Backend : consommateur `SendWelcomeEmailOnUserRegistered` (`auth/` ou `shared/`) abonné à l'événement `UserRegistered`, envoie l'e-mail de façon asynchrone — le Command handler d'inscription ne doit jamais envoyer l'e-mail lui-même ni bloquer la réponse HTTP dessus
- [ ] Frontend : formulaire d'inscription (MUI + validation), formulaire de connexion
- [ ] Frontend : store Zustand `useAuthStore` (token, user, `isAuthenticated`)
- [ ] Frontend : intercepteur Axios ajoutant `Authorization: Bearer <token>`
- [ ] Frontend : route protégée `/dashboard` (guard sur `isAuthenticated`)
- [ ] Tests : tests unitaires sur l'entité `User` (sans DB) ; pytest sur register (nominal + doublon email), login (succès + échec credentials)
- [ ] 🧪 Playwright suggéré : `auth.spec.ts` → inscription → connexion → accès dashboard

**Définition of Done**
- [ ] Aucun mot de passe ou token loggé en clair (vérifier config Sentry/CloudWatch)
- [ ] Endpoint `/health` opérationnel dès cette US (fondation utilisée par US-601)

**Dépendances :** aucune (fondation transversale — à développer en premier)

---

### US-301.5 — Personnalisation des services LLD

**Labels :** `epic:3`, `type:frontend` · **Priorité :** Critique · **Story Points :** 3

**User Story**
En tant que client connecté, je veux sélectionner mes services inclus ou optionnels afin de configurer les prestations de mon contrat de location.

**Critères d'acceptation**
- Given un client sur l'interface de souscription LLD, When il coche une option payante, Then le montant s'ajoute instantanément au calcul du loyer mensuel affiché.
- Given des options sélectionnées, When le client passe à l'étape suivante, Then ces choix sont conservés dans le tunnel de souscription.

**Tâches pour l'agent IA**
- [ ] Frontend : `useSubscriptionTunnelStore` (Zustand) — champ `selectedServices: ServiceSelection[]`
- [ ] Frontend : calcul instantané du loyer total = `monthly_rent + Σ(services payants cochés)` (calcul pur, pas d'appel API — les coûts sont déjà connus côté client via US-102)
- [ ] Frontend : composant `ServiceSelector` (checkboxes MUI, recalcul réactif)
- [ ] Tests : Vitest sur le calcul du total (cas 0, 1, plusieurs services)

**Dépendances :** US-102 (données de services), US-301 (utilisateur connecté)

---

### US-301.6 — Simulation et choix du financement

**Labels :** `epic:3`, `type:frontend` · **Priorité :** Haute · **Story Points :** 3

**User Story**
En tant que client connecté, je veux ajuster mon apport et mon plan de financement afin d'adapter mes mensualités à ma situation budgétaire.

**Critères d'acceptation**
- Given le récapitulatif financier, When le client modifie son apport initial, Then le système recalcule instantanément le plan de financement.
- Given un plan validé, When le client passe à l'étape suivante, Then ces choix sont rattachés au tunnel de souscription.

**Tâches pour l'agent IA**
- [ ] Frontend : slider/input MUI pour l'apport (`down_payment`)
- [ ] Frontend : fonction pure de calcul d'amortissement (mensualité = f(prix véhicule, apport, durée, taux)) — isoler dans `utils/financing.ts` pour testabilité
- [ ] Frontend : ajout de `financingPlan` au store du tunnel
- [ ] ⚠️ Note : le calcul est simulé côté client pour le MVP (pas d'intégration réelle avec un organisme financier). Prévoir un point d'extension backend (`POST /api/v1/financing/simulate`) si une validation serveur devient nécessaire plus tard.
- [ ] Tests : Vitest sur la fonction de calcul (valeurs limites : apport = 0, apport = prix total)

**Dépendances :** US-301.5

---

### US-301.7 — Demande de reprise d'ancien véhicule + création du Dossier

**Labels :** `epic:3`, `type:backend`, `type:frontend` · **Priorité :** Haute · **Story Points :** 3

**User Story**
En tant que client connecté, je veux renseigner mon ancien véhicule et confirmer ma demande afin qu'un dossier soit officiellement créé.

**Contexte technique** — Bounded context `dossiers/`, côté **Command** (CQRS write side).

**Critères d'acceptation**
- Given le formulaire de reprise activé, When le client saisit immatriculation et kilométrage, Then ces données sont conservées pour évaluation future.
- Given l'ensemble des choix (services, financement, reprise) complétés, When le client clique sur « Confirmer ma demande », Then un objet `Dossier` est instancié en base au statut `INITIALIZED`.

**Contrat API**
```
POST /api/v1/dossiers
{
  vehicle_id, type,
  selected_services: [...],
  financing_plan: { down_payment, duration_months },
  trade_in: { registration, mileage, brand?, model? } | null
}
→ 201 { dossier_id, status: "INITIALIZED" }
```

**Tâches pour l'agent IA**
- [ ] Backend : entité métier `Dossier` pure (Aggregate Root) dans `dossiers/domain/entities/Dossier.py`, avec value objects `FinancingPlan` et `TradeIn` (`dossiers/domain/value_objects/`) — méthode de fabrique `Dossier.create(...)` posant le statut initial `INITIALIZED`
- [ ] Backend : modèle `DossierModel` SQLAlchemy dans `dossiers/infrastructure/orm/` + migration Alembic (colonnes embedded pour `financing_plan` et `trade_in`, ou tables séparées liées 1-1)
- [ ] Backend : `DossierMapper.to_domain()` / `to_orm()` dans `dossiers/infrastructure/mappers/`
- [ ] Backend : interface `DossierWriteRepository` (Protocol) dans `dossiers/domain/ports/` — `save()`, `find_by_id()` ; implémentation `SQLAlchemyDossierWriteRepository` dans `dossiers/infrastructure/repositories/`
- [ ] Backend : Command handler `CreateDossierCommand` — dépend de `DossierWriteRepository` (jamais de SQLAlchemy directement) : `Dossier.create(...)` → `repository.save()` → publication événement `DossierInitialized`
- [ ] Backend : **règle métier sur l'entité `Vehicle`** — la disponibilité (`vehicle.is_available()`, déjà définie en US-101) est vérifiée par le Command handler via le `VehicleRepository` ; si indisponible, lever une `DomainError` explicite (ne pas dupliquer la règle ailleurs)
- [ ] Frontend : formulaire de reprise (React Hook Form ou state MUI simple)
- [ ] Frontend : bouton « Confirmer ma demande » → envoi de tout le state du tunnel en un seul appel API, puis `resetTunnelStore()`
- [ ] Tests : tests unitaires sur `Dossier.create()` (sans DB) ; pytest sur la commande (cas véhicule indisponible → `DomainError` → 4xx)

**Dépendances :** US-301.5, US-301.6, US-201/US-202 (vehicle_id valide)

---

### US-302 — Upload de pièces justificatives

**Labels :** `epic:3`, `type:backend`, `type:frontend`, `type:infra` · **Priorité :** Critique · **Story Points :** 8

**User Story**
En tant que client connecté, je veux téléverser mes pièces justificatives afin de constituer mon dossier en ligne.

**Critères d'acceptation**
- Given le client sur « Mon dossier », When il ajoute un fichier PDF/image, Then il est uploadé via React Dropzone et stocké sur S3 via URL pré-signée.
- Given un fichier > 10 Mo, When le client tente de le téléverser, Then un message d'erreur de limite de taille s'affiche.
- Given un document uploadé, When le client revient sur son dossier, Then il voit la liste des documents avec leur statut (En attente / Validé / Refusé).

**Contrat API**
```
POST /api/v1/dossiers/{id}/documents/presigned-url
{ filename, content_type, size, document_type }
→ 200 { document_id, upload_url, s3_key }   (refuse si size > 10Mo → 413)

POST /api/v1/dossiers/{id}/documents/{document_id}/confirm
→ 200 { status: "UPLOADED" }

GET /api/v1/dossiers/{id}/documents
→ [{ id, type, status, uploaded_at }]
```

**Tâches pour l'agent IA**
- [ ] Backend : entité métier `Document` pure dans `dossiers/domain/entities/Document.py` + modèle `DocumentModel` SQLAlchemy dans `dossiers/infrastructure/orm/` + `DocumentMapper` + interface `DocumentRepository` (Protocol) dans `dossiers/domain/ports/` (`save()`, `find_by_id()`, `find_by_dossier()`) et son implémentation SQLAlchemy
- [ ] Backend : bucket S3 privé (Block Public Access ON), configuration boto3
- [ ] Backend : endpoint génération d'URL pré-signée **PUT** (`generate_presigned_url`, `ExpiresIn` court, ex. 300s)
- [ ] Backend : validation taille/type AVANT génération de l'URL (413 si > 10 Mo, 415 si type non autorisé)
- [ ] Backend : `Document` créé au statut `PENDING` avant upload, passe à `UPLOADED` via endpoint `confirm` — le Command handler dépend de `DocumentRepository` et `DossierReadRepository`, jamais de SQLAlchemy directement
- [ ] Backend : **vérification d'appartenance** avant de passer le document à `UPLOADED` — via `dossier.is_owned_by(current_user.id)` sur l'entité `Dossier` (même règle métier que US-304, pas dupliquée en SQL brut)
- [ ] Frontend : intégration React Dropzone, upload direct vers S3 (PUT `upload_url`, pas via l'API backend — évite de saturer FastAPI)
- [ ] Frontend : barre de progression upload, gestion erreur taille
- [ ] Frontend : liste des documents avec badge de statut (MUI Chip)
- [ ] Tests : pytest sur génération d'URL (cas taille limite), test d'intégration confirm (avec/sans propriété du dossier)
- [ ] 🧪 Playwright suggéré : mock de l'upload S3 (intercepter la requête PUT) pour ne pas dépendre d'un vrai bucket en CI

**Dépendances :** US-301.7 (dossier existant)

---

### US-303 — Suivi de l'avancement du dossier

**Labels :** `epic:3`, `type:backend`, `type:frontend` · **Priorité :** Haute · **Story Points :** 3

**User Story**
En tant que client, je veux consulter l'état d'avancement de mon dossier afin d'être informé sans contacter le service commercial.

**Critères d'acceptation**
- Given un dossier en cours, When le client accède à « Mon dossier », Then il voit un indicateur d'avancement (Dossier déposé > En instruction > Décision rendue).
- Given un changement de statut par le back-office, When le client se reconnecte, Then le nouveau statut est visible avec la date de mise à jour.

**Contrat API**
```
GET /api/v1/dossiers/me  → liste des dossiers du client connecté
GET /api/v1/dossiers/{id}/status → { status, updated_at }
```

**Tâches pour l'agent IA**
- [ ] Backend : Query handler `GetMyDossiersQuery` dépendant de `DossierReadRepository` — filtre **obligatoirement** par `client_id == current_user.id` (jamais un `dossier_id` passé librement sans vérification de propriétaire)
- [ ] Backend : endpoint de lecture du statut + timestamp `updated_at`, via le même repository
- [ ] Frontend : composant `DossierStepper` (MUI Stepper) mappant le statut interne (`INITIALIZED`, `DOCUMENTS_PENDING`, `SUBMITTED`, `IN_REVIEW`, `VALIDATED`/`REJECTED`) vers les 3 étapes affichées au client
- [ ] Frontend : React Query avec `refetchInterval` raisonnable (ex. 30s) tant que le dossier n'est pas dans un statut final — noter comme amélioration future : notifications push/websocket plutôt que polling
- [ ] Tests : pytest sur le endpoint status ; Vitest sur le mapping statut → étape visuelle

**Dépendances :** US-301.7, US-302

---

### US-304 — Chiffrement et restriction des accès aux pièces justificatives (RBAC)

**Labels :** `epic:3`, `type:backend`, `type:security` · **Priorité :** Critique · **Story Points :** 5

**User Story**
En tant que RSSI, je veux que les documents clients soient inaccessibles publiquement et soumis à vérification d'identité stricte afin de protéger les données personnelles.

**Critères d'acceptation**
- Given un utilisateur non connecté ou tiers tentant d'accéder directement à l'URL S3, When la requête est reçue, Then une erreur HTTP 403 est renvoyée.
- Given un conseiller ou le propriétaire légitime connecté, When il clique sur « Visualiser le document », Then le back-end génère une URL pré-signée expirant après 60 secondes.

**Contrat API**
```
GET /api/v1/dossiers/{id}/documents/{doc_id}/view-url
→ 200 { url, expires_in: 60 }   (403 si non autorisé)
```

**Tâches pour l'agent IA**
- [ ] Infra : bucket policy S3 refusant tout accès public (aucun ACL public, pas de website hosting sur ce bucket)
- [ ] Backend : service d'autorisation applicatif `can_access_document(user, document)` — s'appuie sur `dossier.is_owned_by(user.id)` (méthode de l'entité `Dossier`) OU `user.role == ADMIN` ; le check métier reste dans le domaine, l'orchestration (comparaison de rôle) reste dans l'application
- [ ] Backend : endpoint `view-url` — appelle `can_access_document` **avant** toute génération d'URL, puis `boto3.generate_presigned_url(..., ExpiresIn=60)` — **objet-level authorization** systématique (protection anti-IDOR : ne jamais faire confiance à l'ID dans l'URL sans vérifier la propriété)
- [ ] Backend : retourner 403 explicite (pas 404, pour respecter le critère d'acceptation) si l'utilisateur n'a pas les droits
- [ ] Tests : pytest — accès propriétaire (200), accès tiers authentifié (403), accès non authentifié (401), expiration après 60s (test avec horloge simulée)

**Dépendances :** US-302

---

### US-305 — Purge automatique des données personnelles (RGPD)

**Labels :** `epic:3`, `type:backend`, `type:infra` · **Priorité :** Haute · **Story Points :** 3

**User Story**
En tant que DPO, je veux que les pièces des dossiers refusés soient supprimées après 30 jours afin de respecter la minimisation RGPD.

**Critères d'acceptation**
- Given un dossier `REJECTED` depuis plus de 30 jours, When le script de purge s'exécute chaque nuit, Then les fichiers S3 sont effacés et les documents passent au statut `PURGED`.

**Tâches pour l'agent IA**
- [ ] Backend : script `purge_rejected_dossiers.py` — utilise `DossierReadRepository` (méthode `find_rejected_since(30)` ou équivalent) plutôt qu'une requête SQL directe, cohérent avec le reste de l'architecture
- [ ] Backend : **pattern non-transactionnel S3 + DB** — une suppression S3 n'est pas transactionnelle avec un update PostgreSQL ; ne jamais faire les deux dans le même bloc en supposant l'atomicité. Séquence : (1) statut document → `PENDING_PURGE` (via `DocumentRepository`), (2) `boto3.delete_object`, (3) statut → `PURGED` seulement si (2) a réussi. Si (2) échoue, le document reste `PENDING_PURGE` et sera repris à la prochaine exécution (idempotent par construction)
- [ ] Infra MVP : exécution via scheduler applicatif simple (APScheduler dans FastAPI) déclenché quotidiennement
- [ ] Infra Production : migration vers **AWS EventBridge Scheduler** déclenchant une tâche ECS planifiée (cohérent avec l'évolution Render → AWS documentée dans l'architecture)
- [ ] Backend : publication événement `DossierPurged`
- [ ] Logging : tracer nombre de dossiers/documents purgés par exécution (CloudWatch)
- [ ] Tests : pytest avec dossiers factices à différentes dates (29j, 30j, 31j) ; test simulant un échec `delete_object` pour vérifier que le document reste bien `PENDING_PURGE` et non `PURGED`

**Dépendances :** US-502 (statut REJECTED existant)

---

## EPIC 4 — Gestion dynamique du stock (Back-office)

### US-401 — Ajout d'un véhicule au catalogue

**Labels :** `epic:4`, `type:backend`, `type:frontend`, `type:security` · **Priorité :** Haute · **Story Points :** 5

**User Story**
En tant qu'administrateur back-office, je veux ajouter un véhicule au catalogue afin de maintenir le stock à jour.

**Critères d'acceptation**
- Given un administrateur connecté, When il remplit le formulaire d'ajout, Then le véhicule apparaît dans le catalogue front-end dans les 30 secondes.
- Given un champ obligatoire manquant, When l'administrateur soumet, Then une erreur de validation s'affiche.

**Contrat API**
```
POST /api/v1/vehicles   (rôle ADMIN requis)
{ brand, model, mileage, price/monthly_rent, photos[], catalog_type }
→ 201 | 422 (validation) | 403 (rôle insuffisant)
```

**Tâches pour l'agent IA**
- [ ] Backend : dépendance FastAPI `require_role(ADMIN)` réutilisable sur toutes les routes back-office
- [ ] Backend : méthode de fabrique `Vehicle.create(...)` sur l'entité (déjà définie en US-101) — le Command handler `AddVehicleCommand` l'appelle puis passe l'instance métier à `VehicleRepository.save()`, jamais de manipulation SQLAlchemy directe
- [ ] Backend : publication événement `VehicleAdded` après sauvegarde réussie
- [ ] Backend : upload photos via même pattern presigned URL que US-302 (réutiliser le composant d'upload)
- [ ] Frontend : formulaire admin (MUI) avec validation Pydantic reflétée côté client
- [ ] Note perf : en MVP (lecture/écriture même base), la propagation « sous 30s » est immédiate ; si un cache CDN/read-model est introduit plus tard, prévoir une invalidation explicite
- [ ] Tests : pytest (nominal, champ manquant, rôle CLIENT refusé → 403)

**Dépendances :** US-301 (auth + rôles)

---

### US-402 — Basculement d'un véhicule entre stocks Vente et Location

**Labels :** `epic:4`, `type:backend`, `type:frontend` · **Priorité :** Haute · **Story Points :** 3

**User Story**
En tant qu'administrateur, je veux basculer un véhicule entre « Vente » et « Location » afin de refléter les décisions commerciales sans dupliquer les données.

**Critères d'acceptation**
- Given un véhicule en stock Vente, When l'administrateur clique « Passer en Location » et confirme, Then il disparaît du catalogue Achat et apparaît en Location.
- Given un véhicule avec un dossier en cours d'instruction, When l'administrateur tente de le basculer, Then une alerte signale le dossier existant et demande confirmation.
- Given un véhicule en stock Location, When l'administrateur bascule vers Vente et confirme, Then il apparaît dans le catalogue Achat.

**Contrat API**
```
PATCH /api/v1/vehicles/{id}/catalog-type
{ new_type, confirm: bool }
→ 200 | 409 { has_active_dossier: true }  (si confirm=false et dossier actif détecté)
```

**Tâches pour l'agent IA**
- [ ] Backend : `require_role(ADMIN)` sur `PATCH /vehicles/{id}/catalog-type` (oublié dans la première version — la logique est déjà en place pour US-401, à répliquer ici)
- [ ] Backend : Command handler `ChangeVehicleCatalogTypeCommand` — appelle `vehicle.switch_to_rental()` ou `vehicle.switch_to_sale()` (méthodes définies dans le modèle de domaine) plutôt que d'assigner directement `catalog_type`, puis `VehicleRepository.save()`
- [ ] Backend : **isolation des bounded contexts** — la vérification "dossier actif sur ce véhicule" interroge le contexte `dossiers/` depuis `véhicules/`. Le Command handler dépend de l'interface `DossierExistencePort` (déjà définie dans le modèle de domaine), jamais du repository de `dossiers/` directement. L'implémentation `DossierExistenceAdapter` (dans `véhicules/infrastructure/adapters/`) s'appuie sur `dossiers/` en interne — ça garde `véhicules/` capable d'évoluer (ou d'être extrait en microservice) sans dépendre du détail d'implémentation de `dossiers/`
- [ ] Backend : publication `VehicleRented` (bascule vers location) ou `VehicleListedForSale` (bascule vers vente — extension proposée)
- [ ] Frontend : modale de confirmation MUI si 409 reçu
- [ ] Tests : pytest — bascule simple, bascule avec dossier actif sans confirm (409), avec confirm (200), rôle CLIENT refusé (403)

**Dépendances :** US-401, US-301.7 (pour détecter les dossiers actifs)

---

## EPIC 5 — Instruction et validation des dossiers

### US-501 — Visualisation des dossiers en attente

**Labels :** `epic:5`, `type:backend`, `type:frontend` · **Priorité :** Haute · **Story Points :** 3

**User Story**
En tant que conseiller commercial ou financier, je veux voir la liste des dossiers en attente afin de prioriser mon travail quotidien.

**Critères d'acceptation**
- Given un conseiller connecté au back-office, When il accède à « Dossiers en attente », Then il voit la liste triée par date de dépôt (client, type, véhicule, statut).
- Given un dossier, When le conseiller clique dessus, Then il consulte toutes les pièces justificatives téléchargées.

**Contrat API**
```
GET /api/v1/dossiers?status=pending&sort=submitted_at   (rôle ADMIN requis)
GET /api/v1/dossiers/{id}   → détail complet + documents
```

**Tâches pour l'agent IA**
- [ ] Backend : définir `PENDING_STATUSES = [SUBMITTED, IN_REVIEW]` — le contrat API utilise `status=pending`, mais le modèle de domaine n'a pas de statut littéral `pending` ; cette liste fait le pont et évite toute ambiguïté dans le Query handler
- [ ] Backend : méthode `find_pending(sort_by)` sur l'interface `DossierReadRepository` (définie dans le modèle de domaine), filtrant sur `PENDING_STATUSES` ; implémentation `SQLAlchemyDossierReadRepository`
- [ ] Backend : Query handler `GetPendingDossiersQuery` — dépend uniquement de `DossierReadRepository`, jamais de SQLAlchemy directement
- [ ] Backend : `require_role(ADMIN)` sur ces routes
- [ ] Frontend : tableau MUI (DataGrid) avec colonnes client/type/véhicule/statut
- [ ] Tests : pytest sur le tri et le filtre de statut

**Dépendances :** US-301.7, US-302

---

### US-502 — Validation ou refus d'un dossier

**Labels :** `epic:5`, `type:backend`, `type:frontend` · **Priorité :** Haute · **Story Points :** 5

**User Story**
En tant que conseiller financier, je veux valider ou refuser un dossier avec commentaire afin de notifier le client de la décision.

**Critères d'acceptation**
- Given un dossier ouvert, When le conseiller clique « Valider » et confirme, Then le statut passe à `VALIDATED` et le client reçoit une notification.
- Given un refus, When le conseiller saisit un motif et clique « Refuser », Then le statut passe à `REJECTED` et le client reçoit le motif par e-mail.
- Given un dossier incomplet, When le conseiller clique « Demander des documents », Then le client reçoit une notification listant les pièces manquantes.

**Contrat API**
```
POST /api/v1/dossiers/{id}/approve  { comment? }
POST /api/v1/dossiers/{id}/reject   { reason }
POST /api/v1/dossiers/{id}/request-documents { missing_documents: [] }
```

**Tâches pour l'agent IA**
- [ ] Backend : `require_role(ADMIN)` sur `POST /approve`, `POST /reject` **et** `POST /request-documents` (les trois routes, pas seulement certaines — c'était couvert sur US-501 mais oublié ici)
- [ ] Backend : Command handlers `ApproveDossierCommand`, `RejectDossierCommand`, `RequestDocumentsCommand` — chacun récupère le `Dossier` via `DossierWriteRepository`, appelle respectivement `dossier.approve(comment)`, `dossier.reject(reason)`, `dossier.request_documents(types)` (méthodes de l'agrégat, définies dans le modèle de domaine), puis `repository.save()`. Ces méthodes lèvent une `DomainError` si la transition est invalide (ex. approuver un dossier déjà `REJECTED`) — la règle de transition vit dans l'agrégat, pas dans le handler
- [ ] Backend : `dossier.reject(reason)` positionne `rejected_at = now()` en interne (nécessaire pour le calcul des 30 jours de US-305)
- [ ] Backend : `RequestDocumentsCommand` valide que chaque `document_type` de `missing_documents` fait partie d'un enum métier `ALLOWED_DOCUMENT_TYPES` (CNI, JUSTIF_DOMICILE, BULLETIN_SALAIRE…) — évite qu'un conseiller demande un type de document qui n'existe pas dans le référentiel
- [ ] Backend : publication `DossierValidated` / `DossierRejected` / `DocumentsRequested` → déclenchement e-mail via Event Bus
- [ ] Frontend : boutons d'action back-office + modale de saisie du motif de refus
- [ ] Tests : tests unitaires sur les méthodes `approve()`/`reject()`/`request_documents()` de l'agrégat (transitions valides et invalides, sans DB) ; pytest d'intégration sur chaque transition + vérification que `rejected_at` est bien positionné + rôle CLIENT refusé (403) sur les 3 routes
- [ ] 🧪 Playwright suggéré : `dossier-review.spec.ts` → connexion admin → validation d'un dossier de test → vérification email (mock)

**Dépendances :** US-501

---

### US-503 — Intégration des données de reprise et de financement

**Labels :** `epic:5`, `type:backend`, `type:frontend` · **Priorité :** Haute · **Story Points :** 5

**User Story**
En tant que conseiller financier, je veux visualiser l'apport, la demande de financement et les caractéristiques du véhicule à reprendre afin d'évaluer la viabilité financière globale du dossier.

**Critères d'acceptation**
- Given un dossier d'achat avec reprise demandée, When le conseiller consulte, Then l'interface affiche l'estimation de reprise, marque, modèle, immatriculation.
- Given un dossier avec plan de financement, When le conseiller consulte la synthèse, Then l'apport, le capital à financer et les mensualités s'affichent clairement.

**Tâches pour l'agent IA**
- [ ] Backend : enrichir le DTO de `GET /api/v1/dossiers/{id}` (déjà créé en US-501) pour inclure les sections `trade_in` et `financing_plan` complètes — le DTO est construit à partir de l'entité métier `Dossier` récupérée via `DossierReadRepository` (donc déjà mappée par `DossierMapper`), **jamais directement depuis `DossierModel`** (le modèle SQLAlchemy ne doit jamais fuiter jusqu'à la couche API)
- [ ] Frontend : section `FinancialSummaryPanel` dans la vue détail dossier back-office (MUI, lecture seule)
- [ ] Tests : pytest sur le DTO enrichi (dossier avec/sans reprise)

**Dépendances :** US-501, US-301.6, US-301.7

---

## EPIC 6 — Architecture cloud, sécurité et résilience

### US-601 — Déploiement automatisé et validation continue (CI/CD)

**Labels :** `epic:6`, `type:infra` · **Priorité :** Critique · **Story Points :** 8

**User Story**
En tant que DevOps, je veux déployer l'application via un pipeline automatisé afin de garantir des mises en production fiables et un uptime optimal.

**Critères d'acceptation**
- Given le pipeline GitHub Actions configuré, When un développeur pousse du code, Then Flake8/Ruff et la suite de tests s'exécutent obligatoirement.
- Given un merge validé sur `main`, When linting et tests sont au vert, Then le déploiement staging se déclenche et s'achève en moins de 5 minutes.
- Given la production active, When le trafic est routé vers la nouvelle version, Then `/health` répond 200.

**Tâches pour l'agent IA**
- [ ] Infra : squelette de dossiers pour les 3 bounded contexts (`auth/`, `véhicules/`, `dossiers/`) + `shared/` — arborescence complète `domain/{entities,value_objects,ports}`, `application/{commands,queries}`, `infrastructure/{orm,mappers,repositories,adapters}`, `api/routers` par contexte, avec `__init__.py` (vide ou docstring d'une ligne). **Aucune logique, aucun modèle, aucun endpoint** à ce stade — uniquement la structure de fichiers, conforme au modèle de domaine de référence en tête de ce document
- [ ] Backend : implémentation du kernel `shared/` — `Entity` de base, `UnitOfWork` (interface + implémentation SQLAlchemy), `EventBus` (interface + implémentation in-memory), exceptions `DomainError`/`NotFoundError`/`ForbiddenError`
- [ ] Infra : `Dockerfile` backend (multi-stage : build deps → image slim runtime)
- [ ] Infra : `Dockerfile` frontend (build React → serve via nginx statique)
- [ ] Infra : `docker-compose.yml` pour environnement local (backend + frontend + PostgreSQL)
- [ ] Backend : configuration du moteur SQLAlchemy (`shared/infrastructure/db.py`) pointant vers le PostgreSQL du `docker-compose` — connexion brute, aucune table requise à ce stade
- [ ] Backend : endpoint `GET /health` (dans `shared/api/`) — exécute un `SELECT 1` via ce moteur pour vérifier la connexion DB (ne dépend d'aucun modèle métier)
- [ ] CI : `.github/workflows/ci.yml` — étapes : `ruff check`, `black --check`, `pytest`, `vitest run`
- [ ] CD : `.github/workflows/cd.yml` — déclenché sur merge `main` → build image → déploiement Render (MVP) ; prévoir variante ECS (build → push ECR → update service) pour la bascule production
- [ ] Tests : valider en local que le pipeline échoue bien si le lint échoue (test négatif volontaire)

**Dépendances :** aucune. Le health check DB ne nécessite que le moteur SQLAlchemy configuré dans cette même US (connexion brute), pas les modèles métier de US-301 — c'est ce qui permet de traiter US-601 en tout premier, sans blocage.

---

### US-602 — Mise en place de la stratégie de sauvegarde (RPO < 5 min)

**Labels :** `epic:6`, `type:infra` · **Priorité :** Critique · **Story Points :** 5

**User Story**
En tant que DevOps, je veux configurer des sauvegardes automatiques PostgreSQL afin de respecter le RPO défini avec le Product Owner.

**Critères d'acceptation**
- Given la base en production, When 5 minutes s'écoulent, Then un point de reprise est disponible via réplication synchrone Multi-AZ, avec rétention 30 jours sur S3.
- Given un snapshot existant, When une restauration d'urgence est effectuée, Then la base est restaurée en état cohérent en moins de 4h (RTO).

**Tâches pour l'agent IA**
- [ ] Infra (IaC) : configuration RDS PostgreSQL Multi-AZ, `backup_retention_period=30`, PITR activé
- [ ] Infra : documenter la distinction technique — le RPO < 5 min est obtenu par **réplication synchrone Multi-AZ + continuous backup PITR** (et non par un snapshot manuel toutes les 5 min, qui serait coûteux et peu pertinent)
- [ ] Infra : script de test de restauration (runbook) — restaurer un snapshot dans un environnement isolé, mesurer le temps réel, comparer au RTO cible
- [ ] Documentation : rédiger le runbook de restauration (procédure pas à pas) dans `docs/runbooks/db-restore.md`

**Dépendances :** US-603 (même périmètre infra DB)

---

### US-603 — Script de migration sécurisé des données historiques

**Labels :** `epic:6`, `type:infra`, `type:backend` · **Priorité :** Critique · **Story Points :** 8

**User Story**
En tant que DevOps, je veux exécuter un ETL de l'ancienne base vers PostgreSQL afin de conserver l'historique d'un million de clients sans interruption de service.

**Critères d'acceptation**
- Given l'ancienne base active, When le script s'exécute en staging, Then 100 % des enregistrements véhicules/clients sont importés.
- Given les données importées, When la migration est achevée, Then elles sont reformatées selon le nouveau schéma sans perte d'intégrité ni de clés étrangères.

**Tâches pour l'agent IA**
- [ ] Backend : script ETL Python (SQLAlchemy Core pour la performance sur gros volumes, pas l'ORM complet)
- [ ] Backend : mode **dry-run** obligatoire avant exécution réelle (log des transformations sans écriture)
- [ ] Backend : traitement par batch (éviter de charger 1M lignes en mémoire d'un coup)
- [ ] Backend : idempotence — upsert basé sur une clé métier stable (permet de relancer le script sans dupliquer)
- [ ] Backend : script de vérification post-migration (compare `COUNT(*)` ancienne base vs nouvelle, vérifie l'absence de clés étrangères orphelines)
- [ ] Infra : exécution sur un environnement de staging isolé (clone RDS) — cohérent avec l'approche Strangler Fig documentée (migration progressive, ancien système non impacté)
- [ ] Logging : rapport de migration détaillé (nombre de lignes migrées, erreurs, durée)

**Dépendances :** US-602 (environnement staging DB)

---

### US-604 — Sécurité périmétrique et protection de l'API (OWASP)

**Labels :** `epic:6`, `type:security`, `type:backend` · **Priorité :** Critique · **Story Points :** 5

**User Story**
En tant que DevOps/RSSI, je veux implémenter des middlewares de sécurité applicative sur FastAPI afin de protéger contre les vulnérabilités web courantes.

**Critères d'acceptation**
- Given un attaquant en force brute sur `/auth/login`, When les échecs dépassent 5/minute, Then son IP est temporairement bloquée (rate limiting).
- Given une requête POST/PUT/DELETE, When le jeton CSRF est absent/invalide, Then l'API rejette avec 403.
- Given un audit de sécurité automatisé, When il s'exécute sur les routes API, Then aucune injection SQL, IDOR ou XSS n'est exploitable.

**⚠️ Clarification technique importante (à trancher avant implémentation)**
L'architecture retenue utilise un **JWT stateless transmis en header `Authorization: Bearer`** (pas de cookie de session). Dans ce modèle, le risque CSRF classique (credentials automatiquement attachés par le navigateur) **ne s'applique pas** à un endpoint qui exige un header Bearer explicite — un site tiers ne peut pas forcer ce header.
- Si le `refresh_token` est stocké en cookie `httpOnly` (pattern recommandé pour limiter l'exposition XSS du refresh token), **alors** une protection CSRF (double-submit cookie ou `SameSite=Strict`) redevient nécessaire, mais uniquement sur l'endpoint de refresh.
- Recommandation : documenter le choix retenu (tokens 100% en mémoire côté client vs refresh en cookie httpOnly) dans le ticket avant que l'agent IA n'implémente le middleware CSRF, pour éviter une protection incohérente avec l'architecture réelle.

**Tâches pour l'agent IA**
- [ ] Backend : middleware de rate limiting sur `/auth/login` (ex. `slowapi`, algorithme sliding window, 5 tentatives/min/IP)
- [ ] Backend : si refresh token en cookie httpOnly → middleware CSRF double-submit sur les routes concernées ; sinon documenter l'absence de nécessité (cf. clarification ci-dessus)
- [ ] Backend : audit anti-IDOR systématique — reprendre le pattern `can_access_document` de US-304 et l'appliquer à **toutes** les ressources appartenant à un utilisateur (dossiers, documents) : vérification d'appartenance avant toute lecture/écriture, jamais uniquement sur la présence d'un ID valide dans l'URL
- [ ] Backend : SQLAlchemy ORM exclusivement (aucune requête SQL brute concaténée) → protection injection SQL par construction
- [ ] Frontend : ne jamais utiliser `dangerouslySetInnerHTML` sans sanitization (React échappe par défaut — vérifier qu'aucun composant ne contourne cette protection)
- [ ] CI : intégrer un scan de sécurité statique (ex. Bandit pour Python) dans le pipeline `US-601`
- [ ] Tests : pytest sur le rate limiting (6e tentative → 429), tests IDOR (utilisateur A ne peut pas lire le dossier de l'utilisateur B)

**Dépendances :** US-301 (JWT), US-304 (pattern d'autorisation objet), US-601 (intégration CI)

---

### US-605 — Observabilité applicative (Sentry + CloudWatch)

**Labels :** `epic:6`, `type:infra`, `type:backend` · **Priorité :** Haute · **Story Points :** 3

**User Story**
En tant que DevOps, je veux instrumenter l'application avec un suivi d'erreurs et des métriques centralisées afin de détecter et diagnostiquer rapidement les incidents en production.

**Critères d'acceptation**
- Given une exception non gérée en production, When elle survient, Then elle est capturée par Sentry avec la stack trace, la route concernée et un ID de corrélation — sans qu'aucune donnée sensible (mot de passe, token, contenu de pièce justificative) ne soit transmise.
- Given les logs applicatifs (API + tâches planifiées type purge RGPD), When ils sont émis, Then ils sont centralisés dans CloudWatch Logs au format structuré (JSON), avec niveau configurable.
- Given un taux d'erreur 5xx anormal ou une latence API dégradée, When un seuil est dépassé, Then une alarme CloudWatch déclenche une notification.

**Tâches pour l'agent IA**
- [ ] Backend : intégrer `sentry-sdk[fastapi]`, DSN injecté via variable d'environnement / Secrets Manager (jamais en dur dans le code)
- [ ] Backend : hook `before_send` Sentry pour scrubber systématiquement les champs sensibles (password, `Authorization`, tokens, contenu de documents) — à valider en cohérence avec US-604
- [ ] Backend : logging structuré JSON (stdlib `logging` + formatter JSON, ou `structlog`) vers stdout — capté nativement par le driver `awslogs` d'ECS Fargate, pas de config CloudWatch manuelle côté code
- [ ] Infra : dashboard CloudWatch (latence p50/p95, taux 5xx, CPU/mémoire des tâches ECS)
- [ ] Infra : alarme CloudWatch (ex. taux d'erreur > 5 % sur 5 min) → notification SNS/e-mail
- [ ] Tests : test d'intégration avec exception simulée (mock du client Sentry) vérifiant qu'aucune donnée sensible ne fuite dans le payload envoyé

**Définition of Done**
- [ ] Vérification manuelle : aucune donnée sensible visible dans un événement Sentry de test
- [ ] Alarme CloudWatch déclenchée volontairement au moins une fois pour valider la notification

**Dépendances :** US-601 (infra de base), US-604 (cohérence sur ce qui doit/ne doit pas être loggé)

---

## 🔄 Ordre de développement recommandé

| Phase | Contenu | US concernées |
|---|---|---|
| 0 — Fondations | Docker, docker-compose, CI de base, `/health` | US-601 (base) |
| 1 — Identité | Inscription/connexion, JWT, rôles | US-301 |
| 2 — Catalogue | Consultation + recherche multimodale | US-101, 102, 201, 202 |
| 3 — Back-office stock | Ajout/bascule véhicules | US-401, 402 |
| 4 — Tunnel de souscription | Services, financement, reprise, création dossier | US-301.5, 301.6, 301.7 |
| 5 — Dossier dématérialisé | Upload, suivi, RBAC documents, purge RGPD | US-302, 303, 304, 305 |
| 6 — Instruction back-office | Visualisation, validation/refus, synthèse financière | US-501, 502, 503 |
| 7 — Résilience & sécurité avancée | Backups, migration historique, OWASP, observabilité | US-602, 603, 604, 605 |

Cet ordre respecte les dépendances techniques identifiées dans chaque ticket et permet d'avoir, dès la phase 3, un MVP démontrable (catalogue + back-office stock) avant d'attaquer la complexité du tunnel de souscription.

---

## 🏷️ Labels & configuration GitHub Projects — récapitulatif

**Labels à créer dans le repo :**
`epic:1` `epic:2` `epic:3` `epic:4` `epic:5` `epic:6` `type:backend` `type:frontend` `type:infra` `type:security` `priority:critique` `priority:haute` `priority:moyenne`

**Milestones suggérés (1 par EPIC) :**
- EPIC 1 — Offre LLD
- EPIC 2 — Recherche multimodale
- EPIC 3 — Dossier dématérialisé
- EPIC 4 — Gestion du stock
- EPIC 5 — Instruction des dossiers
- EPIC 6 — Architecture cloud & sécurité

**Champs custom du Project (Projects v2) :**
- `Priority` (single select)
- `Story Points` (number)
- `Status` (Todo / In Progress / In Review / Done)
- `Sprint` (iteration field, si découpage en sprints)
