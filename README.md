1.1 Sylvester
=============



Version 1.0 de mon bot. Il ne fait pas grand chose pour le moment mais le core principale est bien codé ce qui va me permettre d'ajouter facilement des nouvelles fonctionnalités sans devoir à chaque fois implémenter des nouvelles fonctions et parser des commandes de l'IRC.

### 1.0

* Création automatique d'une configuration avec l'utilisateur si aucune configuration n'existait avant.
* Connexion au serveur IRC ainsi qu'aux différents salons donnés dans la configuration.
* Gestion des arrivés, des départs et des changements de mode.
* Deux commandes disponibles: stop et auth, la première permettant d'arrêter le bot (nécessite d'être OP sur au moins un salon) et la seconde permettant de s'enregistrer de s'authentifier afin de récupérer son mode.
* Une API très simple permettant des actions essentiels comme envoyer un message ou une commande, connaître le mode d'un utilisateur et récupérer des informations stockés dans la configuration (liste des salons, nom du bot, liste des utilisateurs (avec leur préfixe) en fonction du salon).

### 1.1

* Corrections de bug
* Utilisation de Select pour le coeur de la gestion socket
* Ajout d'une feature pour donner les modes à un utilisateur enregistré dynamiquement lorsqu'il rejoint un channel.

### Prévu (mais que je ne compte jamais faire :p)

* Mettre des plugins :D
