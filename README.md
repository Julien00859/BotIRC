# Belzebot - Bot_IRC V3

Belzebot est un client (bot) développé en Python qui permet de gérer l'authentification des utilisateurs sur des channels marqués comme officiel.

## Fonctionnalités
- Connexion à un serveur IRC
- Authentification en temps que Oper (Un OPER appelé Bot doit être activé sur votre serveur)
- Force-OP sur les channels liés (SAMode doit être activé sur votre serveur)
- Enregistrement des nicks des utilisateurs grâce à un mot de passe hashé en SHA-256
- Authentification des nicks des utilisateurs
- Sanction en cas d'échec à l'autentification
- Discution par message privé avec une intelligence artificielle développée par Lymdun (LymOS: http://system.lymdun.fr/ls/)
- Check des URL pour en récupérer le title de la page cible

## Vie privée

Sont sauvegardés les données suivantes:

- Hash du mot de passe défini par l'utilisateur (SHA-256)
- Messages publique envoyés sur les salons à le bot est présent
- Messages privés envoyés au bot
- Commandes IRC

Ne sont pas sauvegardés les données suivantes:

- Mot de passe en clair envoyé par message privé au bot dans le cadre des commandes register et login

Sont envoyés au site web http://system.lymdun.fr/ls/index.php les messages suivant.:

- Messages privés envoyés au bot si ce message n'est pas une commande interne

## Commandes disponible

- `register <mot de passe>`: permet de d'enregistrer le nickname de l'utilisateur
- `login <mot de passe>`: permet d'authentifier le nickname de l'utilisateur
- `islogged <nickname>`: permet de savoir si l'utilisateur est authentifié ou non
- `about`: donne un lien vers cette page
