# MisterSmith - BotIRC V3

MisterSmith est un client (bot) développé en Python qui permet de gérer l'authentification des utilisateurs sur des channels marqués comme officiel.

## Fonctionnalités
- Connexion à un serveur IRC
- Authentification en temps que Oper (Un OPER appelé Bot doit être activé sur votre serveur)
- Force-OP sur les channels liés (SAMode doit être activé sur votre serveur)
- Enregistrement des nicks des utilisateurs grâce à un mot de passe hashé en SHA-256
- Authentification des nicks des utilisateurs
- Sanction en cas d'échec à l'authentification
- Discussion par message privé avec une intelligence artificielle développée par [Lymdun](https://github.com/Lymdun/) (LymOS: http://system.lymdun.fr/ls/)
- Check des URL pour en récupérer le title de la page cible

## Vie privée

Sont sauvegardées les données suivantes:

- Hash du mot de passe défini par l'utilisateur (SHA-256)
- Messages publiques envoyés sur les salons où le bot est présent
- Messages privés envoyés au bot
- Commandes IRC

Ne sont pas sauvegardées les données suivantes:

- Mot de passe en clair envoyé par message privé au bot dans le cadre des commandes register et login

Sont envoyés au site web http://system.lymdun.fr/ls/index.php les messages suivants.:

- Messages privés envoyés au bot si ce message n'est pas une commande interne

## Commandes disponibles

- `register <mot de passe>`: permet d'enregistrer le nickname de l'utilisateur
- `login <mot de passe>`: permet d'authentifier le nickname de l'utilisateur
- `ghost <pseudo> <mot de passe>`: permet de forcer la connexion en temps que `<pseudo>`
- `islogged <nickname>`: permet de savoir si l'utilisateur est authentifié ou non
- `about`: donne un lien vers cette page

## Remerciements

J'aimerais remercier mon ami [Lymdun](https://github.com/Lymdun/) pour m'avoir aidé à intégrer son intelligence artificielle dans mon bot. Remerciement spéciaux à Ikutama, Shiromae, Nabricot et Rozi qui malgré le fait qu'ils pigeaient que puik m'ont quand même aidé de leur mieux et soutenu pendant toute la phase de développement. Un dernier gros kiss à toute la baka juste parce que je vous aime <3
