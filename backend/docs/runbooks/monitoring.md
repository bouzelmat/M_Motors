Supervision AWS M-Motors

Architecture

Le backend FastAPI écrit ses journaux sur la sortie standard et la sortie d'erreur du conteneur. ECS Express Mode utilise la configuration aws_logs_configuration et le groupe CloudWatch /ecs/m-motors-<workspace>/backend pour centraliser ces événements.

Le chemin de supervision est :

Plain Text


FastAPI / Uvicorn
  -> stdout/stderr du conteneur ECS
  -> CloudWatch Logs
  -> filtre de métrique sur le terme "ERROR"
  -> métrique M-Motors/Backend:ApplicationErrorCount
  -> alarme CloudWatch à partir de 5 événements en 300 secondes
  -> sujet SNS m-motors-alerts-<workspace>
  -> e-mail après confirmation de l'abonnement



La configuration est définie dans backend/infra/terraform/monitoring.tf. Le groupe de logs est créé dans ecs_express.tf avec une rétention de 7 jours afin de limiter le coût et de rester adaptée à un environnement d'examen.

Ce qui est compté

Le filtre compte les événements CloudWatch contenant le terme exact ERROR. Il mesure donc des événements de journalisation, et non le nombre de requêtes HTTP 5xx.

Le code FastAPI utilise déjà logger.exception(...) pour les exceptions non gérées. Python/Uvicorn écrit le niveau ERROR dans la ligne de journal et la stack trace est envoyée vers la sortie du conteneur. Aucune modification applicative n'est nécessaire pour ce premier seuil.

Les erreurs métier gérées et les erreurs de validation sont actuellement journalisées au niveau WARNING. Elles ne déclenchent donc pas cette alarme, ce qui évite de confondre les erreurs fonctionnelles attendues avec les exceptions serveur non gérées.

Limitation à connaître : si un message d'exception contient lui-même le mot ERROR, il peut produire un événement supplémentaire. Pour un format de logs strictement déterministe, une évolution ultérieure vers des logs JSON avec un champ level pourrait remplacer ce filtre texte.

Abonnement SNS

Terraform crée un abonnement avec le protocole email vers l'adresse définie par monitoring_alert_email. Terraform ne peut pas confirmer automatiquement cet abonnement. Il faut cliquer sur le lien de confirmation reçu par e-mail avant que SNS transmette les alarmes.

Une subscription en attente de confirmation est normale immédiatement après terraform apply.

Validation Terraform

Depuis la racine du dépôt :

Bash


cd backend/infra/terraform
terraform fmt -check
terraform init
terraform validate
terraform workspace select staging
terraform plan -var='image_tag=TAG_IMAGE'



Ne pas lancer terraform apply sans autorisation explicite. Le plan doit montrer notamment :

•
un groupe CloudWatch Logs ;

•
un filtre de métrique ;

•
une alarme CloudWatch ;

•
un sujet SNS ;

•
un abonnement e-mail SNS.

Application et confirmation

Après autorisation d'application :

Bash


cd backend/infra/terraform
terraform workspace select staging
terraform apply -var='image_tag=TAG_IMAGE'
terraform output monitoring_log_group_name
terraform output monitoring_sns_topic_arn
terraform output monitoring_error_alarm_name



Confirmer ensuite l'abonnement SNS depuis l'e-mail reçu.

Test de bout en bout staging

1.
Déployer une image backend fonctionnelle dans le workspace staging.

2.
Vérifier que le groupe de logs contient les flux ECS :

Bash


aws logs describe-log-streams \
  --log-group-name /ecs/m-motors-staging/backend \
  --order-by LastEventTime \
  --descending \
  --region eu-west-3





3.
Provoquer une erreur contrôlée dans staging, sans utiliser de données sensibles. Par exemple, appeler un endpoint de test explicitement prévu à cet effet ou utiliser une requête non valide provoquant une exception serveur contrôlée. Ne pas ajouter un endpoint de test en production.

4.
Rechercher l'événement ERROR dans CloudWatch Logs :

Bash


aws logs filter-log-events \
  --log-group-name /ecs/m-motors-staging/backend \
  --filter-pattern '"ERROR"' \
  --start-time "$(($(date +%s) - 900))000" \
  --region eu-west-3





5.
Répéter le test jusqu'à obtenir au moins cinq événements distincts dans une fenêtre de cinq minutes, uniquement dans staging.

6.
Vérifier la métrique et l'état de l'alarme :

Bash


aws cloudwatch get-metric-statistics \
  --namespace M-Motors/Backend \
  --metric-name ApplicationErrorCount \
  --dimensions Name=LogGroupName,Value=/ecs/m-motors-staging/backend \
  --statistics Sum \
  --period 300 \
  --start-time "$(date -u -d '15 minutes ago' +%FT%TZ)" \
  --end-time "$(date -u +%FT%TZ)" \
  --region eu-west-3



La transformation de métrique n'ajoute pas de dimension LogGroupName dans cette configuration. Pour la métrique réellement créée, utiliser la commande suivante si la commande dimensionnée ne renvoie rien :

Bash


aws cloudwatch get-metric-statistics \
  --namespace M-Motors/Backend \
  --metric-name ApplicationErrorCount \
  --statistics Sum \
  --period 300 \
  --start-time "$(date -u -d '15 minutes ago' +%FT%TZ)" \
  --end-time "$(date -u +%FT%TZ)" \
  --region eu-west-3





7.
Vérifier le passage de l'alarme à ALARM et la réception de l'e-mail SNS. CloudWatch peut prendre plusieurs minutes pour publier la métrique et changer l'état.

8.
Corriger ou arrêter le scénario de test, puis vérifier que l'alarme repasse à OK après une période sans événement ERROR.

Production et nettoyage

Le même mécanisme est créé par workspace. Il faut donc tester d'abord staging et ne pas provoquer volontairement cinq erreurs en production.

Pour supprimer la supervision avec le reste d'un workspace :

Bash


cd backend/infra/terraform
terraform workspace select production
terraform destroy -target=aws_cloudwatch_metric_alarm.backend_errors \
  -target=aws_cloudwatch_log_metric_filter.backend_errors \
  -target=aws_sns_topic_subscription.alerts_email \
  -target=aws_sns_topic.alerts



La suppression ciblée doit être utilisée avec prudence et seulement dans le cadre d'un nettoyage autorisé. Le groupe CloudWatch est lié à ECS Express Mode et ne doit pas être supprimé séparément si le service l'utilise encore.

Coûts et limites

Les principaux coûts potentiels sont l'ingestion et la conservation CloudWatch Logs, la métrique filtrée, l'alarme CloudWatch et les éventuelles notifications SNS. La rétention de 7 jours et une seule alarme limitent les coûts pour le projet d'examen. Le plan ne crée pas d'alarmes supplémentaires sur les 5xx ou la disponibilité afin de rester minimal ; ces signaux pourraient être ajoutés séparément si le jury exige une distinction entre erreurs applicatives et indisponibilité du service.

