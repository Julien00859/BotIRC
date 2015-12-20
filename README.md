# MrRobot - Bot IRC v4

Un bot IRC écrit en python fournissant une gestion de plugin ainsi qu'une API complète

## Fonctionnalités

- Gestion événementielle de plugins

- API (envoie de commande, de message, liste d'utilisateur (avec leur permission) par salon)

## Plugins proposés

### Essentials:

* Arrête le bot
* Ping-pong
* Affiche une citation tirée de la série MrRobot à la demande
* Modifie le message de topic chaque jour avec une citation aléatoire (de geek évidement)

### url-checker

* Détéction d'une URL dans les message publique
* Envoie d'un message sur le salon pour donner le contenu de la balise "<title>" lié à l'URL

### auth

* Plugin de réservation de nickname
* Gestion dynamique des comptes non-enregistré
* Gel des comptes enregistré
* Administration des comptes par des OP
