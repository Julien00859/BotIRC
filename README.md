# Belzebot - Bot_IRC V3

Belzebot est un client (bot) développé en Python qui permet de gérer l'authentification des utilisateurs sur des channels marqués comme officiel.

## Fonctionnalités
- Connexion à un serveur IRC
- Authentification en temps que Oper (Un OPER appelé Bot doit être activé sur votre serveur)
- Force-OP sur les channels liés (SAMode doit être activé sur votre serveur)
- Enregistrement des nicks des utilisateurs grâce à un mot de passe hashé en SHA-256
- Authentification des nicks des utilisateurs (tout utilisateur se voit attribué le mode VOICE sur tous les salons régit par le bot)
- Sanction en cas d'échec à l'autentification (configurable)

## Vie privée

Sont sauvegardés les données suivantes:

- Mot de passe défini par l'utilisateur enregistré en SHA-256
- Messages publique envoyés sur les salons à le bot est présent
- Messages privés envoyés au bot
- Commandes IRC

Ne sont pas sauvegardés les données suivantes:

- Mot de passe en clair envoyé par message privé au bot dans le cadre des commandes register et login

## Commandes disponible

- `register <mot de passe>`: permet de d'enregistrer le nickname de l'utilisateur
- `login <mot de passe>`: permet d'authentifier le nickname de l'utilisateur
- `islogged <nickname>`: permet de savoir si l'utilisateur est authentifié ou non
- `about`: donne un lien vers cette page
