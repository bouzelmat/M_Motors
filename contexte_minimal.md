
Pour chaque ticket reçu ensuite :
- Se conformer strictement aux choix techniques, à l'architecture et aux standards d'ingénierie décrits ici.
- Ne jamais réinventer une stack, un pattern ou une convention de nommage différente de ce qui est acté plus bas.
- Si un ticket semble entrer en tension avec ce document, **le signaler explicitement** plutôt que d'arbitrer silencieusement (voir section 15 — points de vigilance déjà identifiés).
- Ne pas anticiper l'implémentation de bounded contexts hors du périmètre du ticket courant (ex. ne pas coder `vehicles/` pendant un ticket `auth/`)

## 1. Contexte métier

**M-Motors** — spécialiste de la vente de véhicules d'occasion, fondée en 1987. Après 30 ans d'existence : une des 10 plus grandes entreprises du secteur au niveau national, ~800 employés, ~1 million de clients.

Organisation : Direction générale → Service Commercial, Service Après-Vente, Service Financier, Service IT, Service RH.

Services historiques déjà en place : large catalogue (marques/modèles/motorisations/kilométrage/prix), contrôle qualité des véhicules (contrôles techniques, remise en état, garanties), accompagnement commercial/SAV personnalisé, essai routier avant achat, financement partenaire, reprise de véhicule ancien.

**Déclencheur du projet** : le Service Commercial a mené une étude de terrain + business plan ROI pour un nouveau service **non proposé jusqu'ici** : la **location longue durée (LLD) avec option d'achat**. Projet validé par la direction, budget accordé pour la refonte complète de l'application web. Un Product Owner issu du Service Commercial a été nommé.

La LLD inclut des services en option ou inclus dans l'abonnement :
- Assurance tous risques
- Assistance dépannage
- Entretien et SAV
- Contrôle technique

Si un client est intéressé, il doit s’inscrire pour déposer son dossier d’achat ou de location.
Dans tous les cas, les documents du dossier sont à télécharger depuis l’interface (dossier 100% dématérialisé). Le client peut aussi suivre l’avancement de son dossier depuis son espace client.
---

## 2. Périmètre fonctionnel

### Côté client (interface publique)
- Recherche de véhicules selon deux modes : **achat** ou **location**.
- Si intérêt : le client doit **s'inscrire** puis déposer un **dossier** (achat ou location).
- Dossier **100 % dématérialisé** : tous les documents sont téléversés depuis l'interface.
- Le client **suit l'avancement de son dossier** depuis son espace personnel.

### Côté back-office (interface privée, rôle ADMIN)
- Ajout de véhicules à la location.
- Ajout de véhicules à la vente.
- **Bascule** d'un véhicule location ↔ vente.
- Visualisation des dossiers location/achat.
- Validation ou rejet des dossiers.

### Hors périmètre MVP
- PWA / Mobile (React Native) — prévu en roadmap uniquement, pas dans le MVP.

### Cadrage IT (contraintes posées en amont par le Service IT)
- Définir précisément RPO et RTO avec le Product Owner.
- Retravailler l'architecture logicielle en fonction de ces valeurs.
- Migrer les données actuelles vers la nouvelle base selon l'architecture proposée.
- Hébergement cloud dans le cadre d'une opération planifiée **"Move to Cloud"**.

---

## 3. Cadre académique (pourquoi la rigueur documentaire compte autant que le code)

Projet réalisé dans le cadre d'un Bac+3 (HETIC/Studi), évalué en jury sur plusieurs blocs de compétences, notamment :

- **C1.1** — Spécifier la demande client → produire un document de spécification des besoins qui distingue clairement enjeux métier et objectifs économiques.
- **C1.2** — État de l'art des outils/méthodologies → recommandations argumentées selon coût, faisabilité, délais, performance, pérennité — avec les arbitrages et leurs conséquences explicités.
- **C1.3** — Concevoir l'architecture logicielle et les specs fonctionnelles → schéma d'architecture **obligatoire** (non négociable pour la validation du bloc), nomenclatures univoques, **l'évolutivité doit être le moteur des choix architecturaux**, pas seulement la réponse au besoin immédiat.
- Bloc 2 (dossiers complémentaires) : méthodologie Scrum, stratégie de tests, analyse de risques.

**Conséquence pratique pour l'agent** : chaque choix technique doit rester justifiable (pas seulement fonctionnel), chaque document/diagramme produit a une valeur double (qualité d'ingénierie **et** preuve de compétence pour le jury), et l'évolutivité (ex. monolithe modulaire → microservices) doit transparaître dans la structure du code, pas uniquement dans un document à part.

---

## 4. Choix techniques définitifs (ne pas dévier)

| Domaine | Choix retenu |
|---|---|
| **Frontend** | React 19 + TypeScript, Vite, Material UI (MUI), Zustand (état global), Axios, React Query |
| **Backend** | FastAPI, Python 3.12 (plancher de compatibilité : 3.11+), Poetry |
| **ORM / Migrations** | SQLAlchemy 2.x, Alembic |
| **Validation** | Pydantic / Pydantic Settings |
| **Auth** | JWT + OAuth2 (password flow), bcrypt pour le hachage |
| **Fichiers** | `UploadFile` → upload direct vers S3 via URL pré-signée |
| **Base de données** | PostgreSQL (RDS Multi-AZ en cible cloud) |
| **Déploiement MVP** | Render (coût quasi nul, validation rapide) |
| **Déploiement Production** | AWS (ECS Fargate, RDS, S3, CloudFront) |
| **CI/CD** | GitHub Actions |
| **Conteneurisation** | Docker + Docker Compose |
| **Tests backend** | pytest, httpx, pytest-asyncio |
| **Tests frontend** | Vitest, React Testing Library |
| **Lint/format** | Ruff (lint) + Black (format) |
| **Doc API** | Swagger/OpenAPI (généré automatiquement par FastAPI) |
| **Observabilité** | Sentry (erreurs) + CloudWatch (logs/métriques) |
| **Secrets** | AWS Secrets Manager (jamais de secret en dur ou committé) |
| **Migration données** | Pattern Strangler Fig + Alembic |
| **Architecture** | Monolithe modulaire au démarrage, pensé pour évoluer vers des microservices |
| **API** | REST, découplage total front/back |

---

## 5. Architecture logicielle cible

**Paradigme** : DDD (Domain-Driven Design) + CQRS + Architecture Hexagonale (Ports & Adapters), organisée en **bounded contexts** indépendants au sein d'un monolithe modulaire évolutif.

### Bounded contexts identifiés
- **`auth/`** — authentification, inscription, rôles `CLIENT` / `ADMIN`, JWT.
- **`vehicles/`** — catalogue, recherche, tarification location/vente. Événements : `VehicleAdded`, `VehicleRented`.
- **`dossiers/`** — cycle de vie du dossier client : `DRAFT` → `SUBMITTED` → `VALIDATED` (ou rejeté). Événements : `DossierSubmitted`, `DossierValidated`, `DossierRejected`.
- **`shared/`** — kernel partagé : Entity, Value Object, Aggregate Root, Domain Event, Unit of Work, Event Bus, session SQLAlchemy.

### Principes structurants
- Chaque bounded context : `domain/` (règles métier pures, zéro dépendance framework) → `application/` (orchestration, cas d'usage, DTOs) → `infrastructure/` (DB, JWT, hachage, adapters concrets).
- **CQRS** : séparation explicite lecture/écriture (contrats `Command`, `Query`, `Handler` génériques dans `shared/application/`).
- **Event Bus in-memory** pour le découplage inter-contextes (notifications, emails, analytics) — **évolution prévue et assumée** vers **Outbox Pattern + SQS** pour la résilience, une fois la charge/le besoin de fiabilité augmentés. Ne pas sur-architecturer cette partie prématurément.
- Communication entre couches **uniquement via interfaces/ports**, jamais de dépendance directe à une implémentation concrète.

## 7. Standards d'ingénierie imposés à l'agent IA (transverses, tous sprints)

**Posture** : ingénieur senior + architecte système intransigeant. Maintenabilité, testabilité et robustesse priment toujours sur la rapidité d'écriture.

**Principes de conception**
- SOLID appliqué systématiquement — responsabilité unique par module/classe, dépendance aux abstractions (interfaces/ports) jamais aux implémentations concrètes.
- DRY & KISS — centraliser la logique répétitive, mais **aucune abstraction prématurée** qui lierait artificiellement des domaines distincts. Le code reste explicite.
- Clean Architecture & DDD — séparation stricte Domain (règles métier pures) / Infrastructure (DB, frameworks, API), communication via Ports & Adapters.
- Design Patterns (Repository, Unit of Work, Strategy, Factory) — utilisés pour résoudre un problème précis, **jamais par réflexe**.

**Sécurité et robustesse**
- Security by Design dès la conception.
- Ne jamais faire confiance à une entrée externe : valider, typer, nettoyer systématiquement payloads et requêtes.
- Protection Top 10 OWASP (injections, IDOR, CSRF, failles d'authentification, énumération d'utilisateurs).
- Gestion globale des exceptions : aucune stack trace ou erreur brute ne doit fuiter vers le client.

**Format du code**
- Typage strict — aucun type implicite, aucun `Any`, types précis sur toutes les signatures publiques.
- Nommage opératoire — les noms décrivent exactement la fonction technique ou l'intention métier.
- Docstrings courts (1 à 3 lignes) sur chaque classe/fonction/méthode publique — décrivent **le contrat**, pas le mécanisme interne.
- Commentaires internes réservés au **"pourquoi"** (règle métier non triviale, contournement temporaire obligatoire), jamais au "comment" — que le code doit exprimer par un nommage clair.
- En cas de choix architectural ambigu : documenter l'arbitrage (README ou commentaire "pourquoi") plutôt que de bloquer, sauf si l'ambiguïté empêche réellement d'avancer.

---

## 8. Exigences de sécurité transverses (à appliquer au fil des tickets concernés)

- **Rate limiting** sur `/auth/login` : `slowapi`, sliding window, 5 tentatives/min/IP. *(Défense en profondeur au niveau applicatif — complémentaire, pas redondant, du rate limiting prévu au niveau API Gateway/WAF, voir section 15.)*
- **CSRF — logique conditionnelle** :
  - JWT stateless transmis en header `Authorization: Bearer` → pas de risque CSRF classique (un site tiers ne peut pas forcer ce header).
  - **Si** le refresh token est stocké en cookie httpOnly (pattern recommandé pour limiter l'exposition XSS du refresh token) → protection CSRF (double-submit cookie ou `SameSite=Strict`) redevient nécessaire, **uniquement sur l'endpoint de refresh**.
  - Le choix (tokens 100 % en mémoire côté client vs refresh en cookie httpOnly) doit être documenté **avant** l'implémentation du middleware CSRF, pour éviter une protection incohérente avec l'architecture réelle.
- **Anti-IDOR systématique** : pattern de vérification d'appartenance (`can_access_document`) appliqué à **toutes** les ressources appartenant à un utilisateur (dossiers, documents) — vérification d'appartenance avant toute lecture/écriture, jamais uniquement sur la présence d'un ID valide dans l'URL.
- **SQLAlchemy ORM exclusivement** — aucune requête SQL brute concaténée → protection injection SQL par construction.
- **Frontend** : ne jamais utiliser `dangerouslySetInnerHTML` sans sanitization.
- **CI** : scan de sécurité statique (Bandit pour Python) intégré au pipeline.

---


BACKLOG M-Motors qui permet d'avoir une vue d'ensemble

EPIC 1 — Déploiement de l'offre LLD et services associés
US-101 — Consultation du catalogue LLD
En tant que client, je veux consulter la liste des véhicules disponibles en location longue durée afin de
comparer les offres avant de m'engager.
Critères d'acceptation :
• Given un client sur la page d'accueil, When il sélectionne le mode « Location », Then il voit la liste
des véhicules LLD avec photo, modèle, prix mensuel et services inclus.
• Given un véhicule LLD, When le client clique dessus, Then il voit le détail : assurance, assistance,
entretien, contrôle technique inclus ou en option.
• Given aucun véhicule disponible, When la liste est vide, Then un message « Aucun véhicule
disponible pour le moment » s'affiche.
Estimation : 3 points story | Priorité : Haute
US-102 — Affichage des services optionnels LLD
En tant que client, je veux voir les services disponibles en option (assurance, assistance, entretien, contrôle
technique) pour chaque véhicule en LLD afin d'estimer le coût total de mon abonnement.
Critères d'acceptation :
• Given la fiche d'un véhicule LLD, When les services optionnels sont disponibles, Then chacun est
affiché avec son intitulé et son coût mensuel additionnel.
• Given un service inclus dans l'abonnement, When il est affiché, Then il est clairement labellisé «
Inclus » sans coût additionnel.
Estimation : 2 points story | Priorité : Haute
EPIC 2 — Recherche et consultation multimodale des véhicules
US-201 — Recherche de véhicule par mode Achat
En tant que client, je veux filtrer les véhicules d'occasion à la vente par marque, budget, kilométrage et
motorisation afin de trouver rapidement le véhicule correspondant à mes besoins.
Critères d'acceptation :
• Given le mode « Achat » sélectionné, When le client applique des filtres (ex. budget max 15 000 €,
essence), Then la liste se met à jour en temps réel et n'affiche que les véhicules correspondants.
• Given aucun résultat, When les filtres sont trop restrictifs, Then un message « Aucun véhicule ne
correspond à vos critères » s'affiche avec une suggestion de modifier les filtres.
• Given un véhicule en mode Achat, When le client clique dessus, Then il accède à sa fiche détaillée
(photos, historique, garantie, prix).
Estimation : 5 points story | Priorité : Critique
US-202 — Recherche de véhicule par mode Location
En tant que client, je veux filtrer les véhicules disponibles en LLD par type, durée de contrat et budget
mensuel afin d'identifier les offres adaptées à ma situation.
Critères d'acceptation :
• Given le mode « Location » sélectionné, When le client filtre par budget mensuel (ex. <= 400
€/mois), Then seuls les véhicules dont le loyer de base est inférieur ou égal à 400 € s'affichent.
• Given les deux modes disponibles, When le client passe de « Achat » à « Location », Then
l'interface et les filtres se mettent à jour sans rechargement de page.
Estimation : 5 points story | Priorité : Critique
EPIC 3 — Parcours client et dossier 100 % dématérialisé
US-301 — Inscription et création d'espace client
En tant que visiteur intéressé par un véhicule, je veux créer un compte client afin d'accéder à
l'espace de dépôt de dossier.
• Critères d'acceptation :
• Given un visiteur non connecté cliquant sur « Je suis intéressé », When il remplit le
formulaire d'inscription (email, mot de passe, nom, prénom), Then son compte est
créé et il reçoit un e-mail de confirmation.
• Given un email déjà enregistré, When le visiteur tente de s'inscrire avec le même
email, Then un message d'erreur explicite s'affiche.
• Given un compte créé, When l'utilisateur se connecte, Then il accède à son tableau
de bord personnel.
• Estimation : 3 points story | Priorité : Critique
US-301.5 — Personnalisation des services LLD
En tant que client connecté, je veux sélectionner mes services inclus ou optionnels afin de
configurer les prestations logistiques et d'assurance de mon contrat de location.
• Critères d'acceptation :
• Given un client sur l'interface de souscription LLD, When il coche une option
payante (ex. assurance tous risques, assistance dépannage, entretien, contrôle
technique), Then le montant de l'option s'ajoute instantanément au calcul du loyer
mensuel affiché.
• Given des options sélectionnées, When le client passe à l'étape suivante du tunnel,
Then les identifiants de ces options sont temporairement sauvegardés dans son
panier virtuel.
• Estimation : 3 points story | Priorité : Critique
US-301.6 — Simulation et choix du Financement
En tant que client connecté, je veux ajuster mon apport et mon plan de financement afin d'adapter
mes futures mensualités à ma situation budgétaire.
• Critères d'acceptation :
• Given le récapitulatif financier du véhicule sélectionné, When le client modifie le
montant de son apport initial dans le simulateur, Then le système recalcule
instantanément le plan de financement adapté en partenariat avec les organismes
financiers.
• Given un plan de financement sélectionné et validé, When le client passe à l'étape
suivante, Then ces choix budgétaires sont rattachés temporairement à son panier.
• Estimation : 3 points story | Priorité : Haute
US-301.7 — Demande de reprise d'ancien véhicule
En tant que client connecté possédant un véhicule, je veux renseigner les caractéristiques de ma
voiture actuelle afin de solliciter une offre de reprise pour faciliter mon processus d'achat ou de
location.
• Critères d'acceptation :
• Given le formulaire de reprise activé, When le client saisit l'immatriculation et le
kilométrage de son ancien véhicule, Then le système enregistre ces données pour
permettre l'évaluation commerciale future.
• Given l'ensemble des choix de services, de financement et de reprise complétés,
When le client clique sur le bouton « Confirmer ma demande », Then un objet
"Dossier" global est officiellement instancié en base de données au statut "Initialisé".
• Estimation : 3 points story | Priorité : Haute
US-302 — Upload de pièces justificatives
En tant que client connecté, je veux téléverser mes pièces justificatives (carte d'identité, justificatif
de domicile, bulletins de salaire) afin de constituer mon dossier d'achat ou de location en ligne.
• Critères d'acceptation :
• Given le client sur la page « Mon dossier », When il clique sur « Ajouter un
document » et sélectionne un fichier PDF ou image, Then le fichier est uploadé via
l'interface (React Dropzone) et stocké sur S3 via une URL pré-signée.
• Given un fichier de taille supérieure à 10 Mo, When le client tente de le téléverser,
Then un message d'erreur indique la limite de taille.
• Given un document uploadé, When le client revient sur son dossier, Then il voit la
liste des documents déposés avec leur statut (En attente de validation / Validé /
Refusé).
• Estimation : 8 points story | Priorité : Critique
US-303 — Suivi de l'avancement du dossier
En tant que client, je veux consulter l'état d'avancement de mon dossier d'achat ou de location
depuis mon espace client afin d'être informé sans avoir à contacter le service commercial.
• Critères d'acceptation :
• Given un dossier en cours, When le client accède à « Mon dossier », Then il voit un
indicateur d'avancement avec les étapes : Dossier déposé > En instruction > Décision
rendue.
• Given un changement de statut de son dossier par le back-office, When le client se
reconnecte, Then le nouveau statut est visible avec la date de mise à jour.
• Estimation : 3 points story | Priorité : Haute
US-304 — Chiffrement et restriction des accès aux pièces justificatives (RBAC)
En tant que Responsable Sécurité (RSSI), je veux que les documents téléversés par les clients
soient inaccessibles publiquement et soumis à une vérification d'identité stricte afin de protéger les
données personnelles contre le vol.
• Critères d'acceptation :
• Given un utilisateur non connecté ou un client tiers tentant d'accéder directement à
l'URL S3 d'un document, When la requête est reçue par le stockage, Then une erreur
HTTP 403 (Forbidden) est renvoyée.
• Given un conseiller commercial ou le propriétaire légitime du compte connecté,
When il clique sur "Visualiser le document", Then le back-end génère une URL présignée
dont la validité expire après 60 secondes.
• Estimation : 5 points story | Priorité : Critique
US-305 — Purge automatique des données personnelles (RGPD)
En tant que Délégué à la Protection des Données (DPO), je veux que les pièces justificatives des
dossiers refusés soient automatiquement et définitivement supprimées après 30 jours afin de
respecter la réglementation RGPD sur la minimisation et la conservation des données.
• Critères d'acceptation :
• Given un dossier passé au statut "Refusé" depuis plus de 30 jours, When le script de
purge s'exécute chaque nuit, Then les fichiers PDF/images associés sont effacés du
compartiment S3 et les statuts des documents passent à "Purgé" en base de données.
• Estimation : 3 points story | Priorité : Haute
EPIC 4 — Gestion dynamique du stock (Back-office)
US-401 — Ajout d'un véhicule au catalogue
En tant qu'administrateur back-office, je veux ajouter un véhicule au catalogue (vente ou location) afin de
maintenir le stock à jour.
Critères d'acceptation :
• Given un administrateur connecté, When il remplit le formulaire d'ajout (marque, modèle,
kilométrage, prix, photos, type : Vente ou Location), Then le véhicule apparaît dans le catalogue
front-end dans les 30 secondes.
• Given un champ obligatoire manquant (ex. prix), When l'administrateur soumet le formulaire, Then
un message d'erreur de validation s'affiche.
Estimation : 5 points story | Priorité : Haute
US-402 — Basculement d'un véhicule entre les stocks Vente et Location
En tant qu'administrateur, je veux basculer un véhicule du stock « Vente » vers « Location » ou inversement
afin de refléter les décisions commerciales sans dupliquer les données.
Critères d'acceptation :
• Given un véhicule en stock Vente, When l'administrateur clique sur « Passer en Location » et
confirme, Then le véhicule disparaît du catalogue Achat et apparaît dans le catalogue Location.
• Given un véhicule ayant un dossier en cours d'instruction, When l'administrateur tente de le
basculer, Then une alerte lui signale l'existence du dossier et lui demande de confirmer.
• Given un véhicule en stock Location, When l'administrateur clique sur « Passer en Vente » et
confirme, Then le véhicule disparaît du catalogue Location et apparaît dans le catalogue Achat.
Estimation : 3 points story | Priorité : Haute
EPIC 5 — Instruction et validation des dossiers
US-501 — Visualisation des dossiers en attente
En tant que conseiller commercial ou financier, je veux voir la liste des dossiers clients en attente de
traitement afin de prioriser mon travail quotidien.
Critères d'acceptation :
• Given un conseiller connecté au back-office, When il accède à « Dossiers en attente », Then il voit la
liste triée par date de dépôt avec : nom du client, type de dossier (achat/location), véhicule
concerné, statut.
• Given un dossier, When le conseiller clique dessus, Then il peut consulter toutes les pièces
justificatives téléchargées par le client.
Estimation : 3 points story | Priorité : Haute
US-502 — Validation ou refus d'un dossier
En tant que conseiller financier, je veux valider ou refuser un dossier client avec un commentaire afin de
notifier le client de la décision prise.
Critères d'acceptation :
• Given un dossier ouvert, When le conseiller clique sur « Valider » et confirme, Then le statut du
dossier passe à « Approuvé » et le client reçoit une notification.
• Given un refus, When le conseiller saisit un motif et clique sur « Refuser », Then le statut passe à «
Refusé » et le client reçoit le motif par e-mail.
• Given un dossier incomplet, When le conseiller clique sur « Demander des documents », Then le
client reçoit une notification listant les pièces manquantes.
Estimation : 5 points story | Priorité : Haute
US-503 — Intégration des données de reprise et de financement
En tant que conseiller financier, je veux visualiser le montant de l'apport, la
demande de financement et les caractéristiques du véhicule à reprendre afin
d'évaluer la viabilité financière globale du dossier.
Critères d'acceptation :
• Given un conseiller consultant un dossier d'achat, When le client a demandé
une reprise d'ancien véhicule, Then l'interface affiche l'estimation de la
reprise, la marque, le modèle et l'immatriculation du véhicule concerné.
• Given un dossier client incluant un plan de financement, When le conseiller
consulte la synthèse financière, Then l'interface affiche clairement le montant
de l'apport, le capital à financer et les mensualités prévues
Estimation : 5 Story Points | Priorité : Haute
EPIC 6 — Architecture cloud, sécurité et résilience
US-601 — Déploiement automatisé et validation continue (CI/CD)
En tant que DevOps, je veux déployer l'application (FastAPI + React + PostgreSQL) sur une
infrastructure cloud (Render pour le MVP) via un pipeline automatisé afin de garantir des mises en
production fiables et un uptime optimal.
• Critères d'acceptation :
• Given le pipeline CI/CD GitHub Actions configuré, When un développeur pousse
du code, Then les étapes d'analyse statique (linter Flake8) et la suite de tests
automatisés s'exécutent obligatoirement.
• Given un merge validé sur la branche main, When toutes les étapes de linting et de
tests sont au vert, Then le déploiement sur l'environnement de staging se déclenche
automatiquement et s'achève en moins de 5 minutes.
• Given l'environnement de production actif, When le trafic est routé vers la nouvelle
version, Then les sondes de disponibilité (health checks) répondent avec un code
HTTP 200 sur la route /health.
• Estimation : 8 points story | Priorité : Critique
US-602 — Stratégie de sauvegarde et restauration PostgreSQL
En tant que DevOps, je veux definir et tester une strategie de sauvegarde adaptee au fournisseur PostgreSQL de chaque environnement, afin de respecter les objectifs RPO/RTO valides avec le Product Owner.
• Critères d'acceptation :
• Les capacites, la frequence, la retention et les limites de sauvegarde de Render pour le MVP et de RDS pour la cible AWS sont documentees. Un RPO inferieur a 5 minutes et un RTO inferieur a 4 heures restent des objectifs a confirmer, et non des garanties presumees.
• La configuration RDS cible distingue haute disponibilite Multi-AZ, sauvegardes automatisees et PITR. Les sauvegardes gerees par RDS ne sont pas presentees comme des snapshots toutes les 5 minutes ni comme des objets du bucket S3 applicatif.
• Un exercice en environnement isole restaure un point choisi, mesure le temps et verifie l'integrite sans modifier ni supprimer la base source.
• Le runbook de restauration, la mesure du RTO et les ecarts constates sont documentes dans `docs/tickets/US-602.md`.
• Estimation : 5 points story | Priorité : Critique
US-603 — Script de migration sécurisé des données historiques (1987-2026)
En tant que DevOps, je veux exécuter un script d'extraction, transformation et chargement (ETL)
de l'ancienne base de données vers PostgreSQL afin de conserver l'historique d'un million de clients
sans interruption de service.
• Critères d'acceptation :
• Given l'ancienne base de données M-Motors active, When le script de migration
s'exécute dans l'environnement de staging, Then 100 % des enregistrements de
véhicules et de clients existants sont importés.
• Given les données importées, When la migration est achevée, Then les données sont
reformatées selon le nouveau schéma relationnel PostgreSQL sans aucune perte
d'intégrité ni de clés étrangères.
• Estimation : 8 points story | Priorité : Critique
US-604 — Sécurité périmétrique et protection de l'API (OWASP)
En tant que DevOps / RSSI, je veux implémenter des middlewares de sécurité applicative sur le
back-end FastAPI afin de protéger l'infrastructure contre les vulnérabilités web courantes et les
attaques automatisées.
• Critères d'acceptation :
• Given un attaquant tentant une attaque par force brute sur le point de terminaison
d'authentification, When les échecs dépassent 5 tentatives par minute, Then son
adresse IP est temporairement bloquée par le mécanisme de Rate Limiting.
• Given une requête entrante modifiant l'état du système (POST/PUT/DELETE),
When le jeton de sécurité CSRF est absent, malformé ou invalide, Then l'API rejette
immédiatement la requête avec un code HTTP 403.
• Given l'application déployée, When un audit de sécurité automatisé est exécuté sur
les routes de l'API, Then aucune faille critique d'injection SQL, d'IDOR (Insecure
Direct Object Reference) ou de type XSS n'est exploitable.
• Estimation : 5 points story | Priorité : Critique


