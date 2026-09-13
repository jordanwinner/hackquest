# Missions organisées par catégorie
# Chaque mission a : id, titre, histoire, tâches, xp, hints, unlock

MISSIONS = {

    # ─────────────────────────────────────────────
    # CATÉGORIE 1 : LINUX BASICS
    # ─────────────────────────────────────────────
    "linux_basics": {
        "title": "🐧 Linux Basics",
        "description": "Maîtrise les commandes fondamentales de Linux.",
        "missions": [

            {
                "id": "lb_01",
                "title": "Premier Contact",
                "story": (
                    "Tu viens d'atterrir sur un serveur inconnu.\n"
                    "Tout est sombre. Tu dois d'abord savoir où tu es."
                ),
                "objective": "Affiche le répertoire courant.",
                "expected_cmd": ["pwd"],
                "accept_contains": ["pwd"],
                "xp": 10,
                "hints": [
                    "La commande affiche le 'Print Working Directory'.",
                    "Elle s'écrit en 3 lettres : p-w-d",
                ],
                "unlocks": [],
            },
            {
                "id": "lb_02",
                "title": "Exploration",
                "story": (
                    "Tu es dans un répertoire. Des fichiers se cachent ici.\n"
                    "Liste ce qu'il y a autour de toi."
                ),
                "objective": "Liste le contenu du répertoire courant.",
                "expected_cmd": ["ls", "ls -l", "ls -la", "ls -a"],
                "accept_contains": ["ls"],
                "xp": 10,
                "hints": [
                    "2 lettres. Pense à 'LiSt'.",
                    "La commande est : ls",
                ],
                "unlocks": [],
            },
            {
                "id": "lb_03",
                "title": "Changer de Territoire",
                "story": (
                    "Tu vois un dossier suspect nommé 'secret'.\n"
                    "Tu dois t'y déplacer pour fouiller."
                ),
                "objective": "Navigue dans un dossier avec la bonne commande.",
                "expected_cmd": ["cd"],
                "accept_contains": ["cd"],
                "xp": 10,
                "hints": [
                    "Pense à 'Change Directory'.",
                    "La commande est : cd <dossier>",
                ],
                "unlocks": [],
            },
            {
                "id": "lb_04",
                "title": "Lire le Message",
                "story": (
                    "Tu trouves un fichier 'message.txt'.\n"
                    "Il contient peut-être des indices cruciaux."
                ),
                "objective": "Affiche le contenu d'un fichier texte.",
                "expected_cmd": ["cat message.txt", "cat"],
                "accept_contains": ["cat"],
                "xp": 15,
                "hints": [
                    "La commande ressemble à un animal.",
                    "cat <fichier> affiche son contenu.",
                ],
                "unlocks": [],
            },
            {
                "id": "lb_05",
                "title": "Chercher la Trace",
                "story": (
                    "Des milliers de logs. Quelque part, le mot 'BREACH' se cache.\n"
                    "Tu dois le trouver rapidement."
                ),
                "objective": "Cherche un mot dans un fichier avec grep.",
                "expected_cmd": ["grep"],
                "accept_contains": ["grep"],
                "xp": 20,
                "hints": [
                    "L'outil de recherche de texte dans Linux s'appelle grep.",
                    "Syntaxe : grep 'mot' fichier",
                ],
                "unlocks": [],
            },
            {
                "id": "lb_06",
                "title": "Trouver le Fichier Perdu",
                "story": (
                    "Un fichier nommé 'credentials.txt' existe quelque part\n"
                    "dans le système. Mais où ?"
                ),
                "objective": "Trouve un fichier dans le système.",
                "expected_cmd": ["find"],
                "accept_contains": ["find"],
                "xp": 20,
                "hints": [
                    "La commande pour chercher des fichiers dans Linux.",
                    "Syntaxe : find / -name 'fichier'",
                ],
                "unlocks": [],
            },
            {
                "id": "lb_07",
                "title": "Qui Suis-je ?",
                "story": (
                    "Tu es infiltré sur le serveur mais tu ne sais pas\n"
                    "sous quelle identité tu opères."
                ),
                "objective": "Affiche l'utilisateur courant.",
                "expected_cmd": ["whoami", "id"],
                "accept_contains": ["whoami", "id"],
                "xp": 10,
                "hints": [
                    "La commande demande littéralement 'who am i'.",
                    "whoami ou id",
                ],
                "unlocks": [],
            },
            {
                "id": "lb_08",
                "title": "Les Permissions",
                "story": (
                    "Un fichier critique est là mais tu n'as pas les droits.\n"
                    "Tu dois comprendre les permissions avant d'agir."
                ),
                "objective": "Affiche les permissions détaillées d'un fichier.",
                "expected_cmd": ["ls -l", "ls -la", "stat"],
                "accept_contains": ["ls -l", "stat"],
                "xp": 25,
                "hints": [
                    "ls avec une option pour le format long.",
                    "ls -l <fichier> ou stat <fichier>",
                ],
                "unlocks": [],
            },
            {
                "id": "lb_09",
                "title": "Pipeline d'Espion",
                "story": (
                    "Tu as un énorme fichier de logs. Tu veux les 10 dernières lignes\n"
                    "et filtrer celles qui contiennent 'ERROR'."
                ),
                "objective": "Combine tail et grep avec un pipe.",
                "expected_cmd": ["tail", "grep", "|"],
                "accept_contains": ["|"],
                "xp": 30,
                "hints": [
                    "Le symbole | permet de chaîner des commandes.",
                    "Exemple : tail -n 10 fichier | grep 'ERROR'",
                ],
                "unlocks": [],
            },
            {
                "id": "lb_10",
                "title": "Processus Fantôme",
                "story": (
                    "Quelque chose tourne en arrière-plan sur ce serveur.\n"
                    "Tu dois voir tous les processus actifs."
                ),
                "objective": "Liste tous les processus en cours.",
                "expected_cmd": ["ps", "ps aux", "top", "htop"],
                "accept_contains": ["ps", "top", "htop"],
                "xp": 20,
                "hints": [
                    "ps ou top pour voir les processus.",
                    "ps aux affiche tous les processus.",
                ],
                "unlocks": ["recon"],
            },
        ],
    },

    # ─────────────────────────────────────────────
    # CATÉGORIE 2 : RECON
    # ─────────────────────────────────────────────
    "recon": {
        "title": "🔍 Reconnaissance",
        "description": "Apprends à scanner, énumérer et collecter des infos.",
        "missions": [

            {
                "id": "rc_01",
                "title": "Premier Scan",
                "story": (
                    "Une cible : 10.10.10.5\n"
                    "Tu ne sais rien sur elle. Commence par un scan basique."
                ),
                "objective": "Lance un scan nmap basique sur une IP.",
                "expected_cmd": ["nmap"],
                "accept_contains": ["nmap"],
                "xp": 30,
                "hints": [
                    "nmap est l'outil de scan réseau numéro 1.",
                    "Syntaxe : nmap <ip>",
                ],
                "unlocks": [],
            },
            {
                "id": "rc_02",
                "title": "Scan Agressif",
                "story": (
                    "Le scan basique a montré des ports ouverts.\n"
                    "Tu veux détails : versions des services, OS, scripts."
                ),
                "objective": "Lance un scan nmap avec détection de version et scripts.",
                "expected_cmd": ["nmap -sV", "nmap -A", "nmap -sC"],
                "accept_contains": ["nmap -sV", "nmap -A", "nmap -sC", "nmap -"],
                "xp": 40,
                "hints": [
                    "L'option -A active la détection agressive.",
                    "nmap -A -sV <ip> — détecte OS + versions + scripts.",
                ],
                "unlocks": [],
            },
            {
                "id": "rc_03",
                "title": "Sous-domaines Cachés",
                "story": (
                    "Le domaine target.com cache des sous-domaines.\n"
                    "Ton arsenal a plusieurs outils pour ça."
                ),
                "objective": "Énumère les sous-domaines d'un domaine.",
                "expected_cmd": ["subfinder", "amass", "subdomains", "dnsrecon"],
                "accept_contains": ["subfinder", "amass", "subdomains", "dnsrecon"],
                "xp": 40,
                "hints": [
                    "Ton arsenal a subfinder, amass, subdomains...",
                    "subfinder -d target.com — rapide et efficace.",
                ],
                "unlocks": [],
            },
            {
                "id": "rc_04",
                "title": "OSINT : Qui est-il ?",
                "story": (
                    "Un utilisateur : 'darkwolf99'\n"
                    "Tu dois retrouver sa présence sur tous les réseaux."
                ),
                "objective": "Recherche un username sur toutes les plateformes.",
                "expected_cmd": ["sherlock", "whatsmyname", "maigret", "osint"],
                "accept_contains": ["sherlock", "whatsmyname", "maigret", "osint"],
                "xp": 35,
                "hints": [
                    "Ton arsenal a sherlock, maigret, whatsmyname.",
                    "sherlock darkwolf99 — cherche sur 300+ sites.",
                ],
                "unlocks": [],
            },
            {
                "id": "rc_05",
                "title": "Récolte d'Emails",
                "story": (
                    "La cible est company.com.\n"
                    "Tu as besoin d'adresses email pour la prochaine phase."
                ),
                "objective": "Collecte des emails liés à un domaine.",
                "expected_cmd": ["theHarvester", "osint", "h8mail"],
                "accept_contains": ["theHarvester", "osint", "h8mail"],
                "xp": 40,
                "hints": [
                    "theHarvester est l'outil classique pour ça.",
                    "theHarvester -d company.com -b google",
                ],
                "unlocks": ["web"],
            },
        ],
    },

    # ─────────────────────────────────────────────
    # CATÉGORIE 3 : WEB
    # ─────────────────────────────────────────────
    "web": {
        "title": "🌐 Web Hacking",
        "description": "Attaques web : SQLi, XSS, fuzzing et plus.",
        "missions": [

            {
                "id": "web_01",
                "title": "Cartographie du Site",
                "story": (
                    "http://target.com est en ligne.\n"
                    "Tu dois trouver les répertoires et fichiers cachés."
                ),
                "objective": "Fuzz les répertoires d'un site web.",
                "expected_cmd": ["gobuster", "ffuf", "dirb", "feroxbuster", "fuzz"],
                "accept_contains": ["gobuster", "ffuf", "dirb", "feroxbuster", "fuzz"],
                "xp": 40,
                "hints": [
                    "gobuster, ffuf, dirb sont dans ton arsenal.",
                    "gobuster dir -u http://target.com -w wordlist.txt",
                ],
                "unlocks": [],
            },
            {
                "id": "web_02",
                "title": "Injection SQL",
                "story": (
                    "Un formulaire de login suspect.\n"
                    "Le développeur n'a peut-être pas sécurisé ses requêtes SQL."
                ),
                "objective": "Teste une injection SQL sur un paramètre.",
                "expected_cmd": ["sqlmap", "sqli"],
                "accept_contains": ["sqlmap", "sqli"],
                "xp": 50,
                "hints": [
                    "sqlmap automatise les injections SQL.",
                    "sqlmap -u 'http://target.com/login?id=1' --dbs",
                ],
                "unlocks": [],
            },
            {
                "id": "web_03",
                "title": "XSS : Vol de Cookie",
                "story": (
                    "Un champ de recherche sur target.com.\n"
                    "Injecte un script pour voler le cookie de session."
                ),
                "objective": "Détecte une faille XSS.",
                "expected_cmd": ["dalfox", "xsstrike", "xss"],
                "accept_contains": ["dalfox", "xsstrike"],
                "xp": 50,
                "hints": [
                    "dalfox et xsstrike scannent les XSS.",
                    "dalfox url 'http://target.com/search?q=test'",
                ],
                "unlocks": [],
            },
            {
                "id": "web_04",
                "title": "JWT Forgé",
                "story": (
                    "L'application utilise des JWT pour l'auth.\n"
                    "Analyse le token et tente de le forger."
                ),
                "objective": "Analyse et forge un JWT.",
                "expected_cmd": ["jwt-tool"],
                "accept_contains": ["jwt-tool"],
                "xp": 60,
                "hints": [
                    "jwt-tool est dans ton arsenal.",
                    "jwt-tool <token> -T pour le tester.",
                ],
                "unlocks": [],
            },
            {
                "id": "web_05",
                "title": "Scanner de Vulns",
                "story": (
                    "Avant d'aller plus loin, fais un scan complet\n"
                    "des vulnérabilités web connues sur la cible."
                ),
                "objective": "Lance un scan de vulnérabilités web.",
                "expected_cmd": ["nikto", "nuclei"],
                "accept_contains": ["nikto", "nuclei"],
                "xp": 45,
                "hints": [
                    "nikto et nuclei sont tes scanners web.",
                    "nikto -h http://target.com",
                ],
                "unlocks": ["exploitation"],
            },
        ],
    },

    # ─────────────────────────────────────────────
    # CATÉGORIE 4 : EXPLOITATION
    # ─────────────────────────────────────────────
    "exploitation": {
        "title": "💥 Exploitation",
        "description": "Reverse shells, Metasploit, exploitation de vulnérabilités.",
        "missions": [

            {
                "id": "ex_01",
                "title": "Reverse Shell",
                "story": (
                    "Tu as une RCE sur la cible.\n"
                    "Il te faut un reverse shell pour prendre le contrôle."
                ),
                "objective": "Génère un reverse shell.",
                "expected_cmd": ["revshell", "msfvenom"],
                "accept_contains": ["revshell", "msfvenom"],
                "xp": 60,
                "hints": [
                    "revshell génère des one-liners de reverse shell.",
                    "revshell ou msfvenom -p cmd/unix/reverse_bash",
                ],
                "unlocks": [],
            },
            {
                "id": "ex_02",
                "title": "Catcher le Shell",
                "story": (
                    "Tu as lancé le payload. Maintenant tu dois écouter\n"
                    "la connexion entrante et stabiliser le shell."
                ),
                "objective": "Lance un listener et stabilise le shell.",
                "expected_cmd": ["catch", "nc -lvnp", "ncat"],
                "accept_contains": ["catch", "nc", "ncat"],
                "xp": 50,
                "hints": [
                    "catch dans ton arsenal automatise ça.",
                    "catch 4444 ou nc -lvnp 4444",
                ],
                "unlocks": [],
            },
            {
                "id": "ex_03",
                "title": "Metasploit : Premier Exploit",
                "story": (
                    "La cible tourne sur Windows avec EternalBlue non patché.\n"
                    "Lance Metasploit et exploite-la."
                ),
                "objective": "Utilise Metasploit pour exploiter une cible.",
                "expected_cmd": ["msfconsole"],
                "accept_contains": ["msfconsole"],
                "xp": 80,
                "hints": [
                    "msfconsole lance Metasploit.",
                    "use exploit/windows/smb/ms17_010_eternalblue",
                ],
                "unlocks": [],
            },
            {
                "id": "ex_04",
                "title": "Chercher un Exploit",
                "story": (
                    "Service inconnu sur le port 8080 : version 2.3.4.\n"
                    "Cherche s'il existe un exploit public."
                ),
                "objective": "Recherche un exploit dans les bases de données.",
                "expected_cmd": ["searchsploit", "exploit-search"],
                "accept_contains": ["searchsploit", "exploit-search"],
                "xp": 40,
                "hints": [
                    "searchsploit cherche dans ExploitDB.",
                    "searchsploit <service> <version>",
                ],
                "unlocks": ["post_exploit"],
            },
        ],
    },

    # ─────────────────────────────────────────────
    # CATÉGORIE 5 : POST-EXPLOITATION
    # ─────────────────────────────────────────────
    "post_exploit": {
        "title": "🏠 Post-Exploitation",
        "description": "Privesc, pillage, persistance et mouvement latéral.",
        "missions": [

            {
                "id": "pe_01",
                "title": "Élévation de Privilèges",
                "story": (
                    "Tu es sur la machine en tant que 'www-data'.\n"
                    "Tu dois devenir root. Cherche les vecteurs de privesc."
                ),
                "objective": "Analyse les vecteurs de privesc Linux.",
                "expected_cmd": ["privesc-check", "linpeas", "sudo -l"],
                "accept_contains": ["privesc-check", "linpeas", "sudo"],
                "xp": 80,
                "hints": [
                    "privesc-check dans ton arsenal fait ça automatiquement.",
                    "sudo -l liste ce que tu peux exécuter en root.",
                ],
                "unlocks": [],
            },
            {
                "id": "pe_02",
                "title": "Pillage de Secrets",
                "story": (
                    "Tu es root. Maintenant trouve tous les mots de passe,\n"
                    "clés SSH, tokens cachés dans le système."
                ),
                "objective": "Trouve les secrets et credentials cachés.",
                "expected_cmd": ["loot"],
                "accept_contains": ["loot"],
                "xp": 60,
                "hints": [
                    "loot dans ton arsenal cherche automatiquement les secrets.",
                    "loot — scanne le système pour credentials, clés, tokens.",
                ],
                "unlocks": [],
            },
            {
                "id": "pe_03",
                "title": "Persistance",
                "story": (
                    "Tu as le contrôle mais le serveur peut rebooter.\n"
                    "Installe une backdoor pour maintenir l'accès."
                ),
                "objective": "Établis la persistance sur la machine.",
                "expected_cmd": ["persistence"],
                "accept_contains": ["persistence"],
                "xp": 70,
                "hints": [
                    "persistence dans ton arsenal génère des one-liners.",
                    "crontab, ~/.bashrc, services systemd...",
                ],
                "unlocks": ["crypto"],
            },
        ],
    },

    # ─────────────────────────────────────────────
    # CATÉGORIE 6 : CRYPTO
    # ─────────────────────────────────────────────
    "crypto": {
        "title": "🔐 Cryptographie",
        "description": "Décoder, casser, attaquer les chiffrements.",
        "missions": [

            {
                "id": "cr_01",
                "title": "Identifier le Hash",
                "story": (
                    "Tu trouves ce hash : 5f4dcc3b5aa765d61d8327deb882cf99\n"
                    "C'est quoi ? Et comment le casser ?"
                ),
                "objective": "Identifie le type de hash.",
                "expected_cmd": ["hashid", "hashit"],
                "accept_contains": ["hashid", "hashit"],
                "xp": 30,
                "hints": [
                    "hashid identifie le type de hash.",
                    "hashid '5f4dcc3b5aa765d61d8327deb882cf99'",
                ],
                "unlocks": [],
            },
            {
                "id": "cr_02",
                "title": "Casser le Hash",
                "story": (
                    "C'est un MD5. Tu dois le casser avec une wordlist."
                ),
                "objective": "Craque un hash MD5 avec hashcat ou john.",
                "expected_cmd": ["hashcat", "john"],
                "accept_contains": ["hashcat", "john"],
                "xp": 50,
                "hints": [
                    "hashcat -m 0 pour MD5.",
                    "hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt",
                ],
                "unlocks": [],
            },
            {
                "id": "cr_03",
                "title": "Magie d'Encodage",
                "story": (
                    "Un message bizarre : 'SGVsbG8gV29ybGQ='\n"
                    "Décode-le et trouve le message caché."
                ),
                "objective": "Décode un message encodé en Base64.",
                "expected_cmd": ["b64", "encode", "magic", "base64"],
                "accept_contains": ["b64", "encode", "magic", "base64"],
                "xp": 25,
                "hints": [
                    "Le = à la fin indique souvent du Base64.",
                    "b64 ou echo 'SGVsbG8gV29ybGQ=' | base64 -d",
                ],
                "unlocks": [],
            },
            {
                "id": "cr_04",
                "title": "RSA Faible",
                "story": (
                    "Un serveur utilise RSA avec de petits facteurs premiers.\n"
                    "Factorise la clé et déchiffre le message."
                ),
                "objective": "Attaque une clé RSA faible.",
                "expected_cmd": ["rsa", "rsa-tool"],
                "accept_contains": ["rsa", "rsa-tool"],
                "xp": 80,
                "hints": [
                    "rsa dans ton arsenal gère factordb, wiener, fermat...",
                    "rsa --fermat ou rsa --factordb",
                ],
                "unlocks": ["forensics"],
            },
        ],
    },

    # ─────────────────────────────────────────────
    # CATÉGORIE 7 : FORENSICS
    # ─────────────────────────────────────────────
    "forensics": {
        "title": "🔬 Forensics",
        "description": "Analyse de fichiers, stéganographie, PCAP, mémoire.",
        "missions": [

            {
                "id": "fo_01",
                "title": "Image Suspecte",
                "story": (
                    "Une image PNG t'a été envoyée.\n"
                    "Quelque chose est caché dedans. Analyse-la."
                ),
                "objective": "Analyse les métadonnées et secrets d'une image.",
                "expected_cmd": ["metadata", "exiftool", "stego", "zsteg"],
                "accept_contains": ["metadata", "exiftool", "stego", "zsteg", "binwalk"],
                "xp": 40,
                "hints": [
                    "metadata ou exiftool pour les métadonnées.",
                    "zsteg pour la stéganographie LSB dans PNG.",
                ],
                "unlocks": [],
            },
            {
                "id": "fo_02",
                "title": "Analyse PCAP",
                "story": (
                    "Tu as capturé le trafic réseau de la cible.\n"
                    "Trouve ce qui a été transmis dans ce PCAP."
                ),
                "objective": "Analyse un fichier PCAP.",
                "expected_cmd": ["pcap", "wireshark", "tshark"],
                "accept_contains": ["pcap", "wireshark", "tshark"],
                "xp": 50,
                "hints": [
                    "pcap dans ton arsenal analyse automatiquement.",
                    "tshark -r capture.pcap ou wireshark pour le GUI.",
                ],
                "unlocks": [],
            },
            {
                "id": "fo_03",
                "title": "Mémoire Volatile",
                "story": (
                    "Un dump mémoire d'un système compromis.\n"
                    "Extrais les processus et credentials de la RAM."
                ),
                "objective": "Analyse un dump mémoire avec Volatility.",
                "expected_cmd": ["vol3", "volatility3", "memforensics"],
                "accept_contains": ["vol3", "volatility3", "memforensics"],
                "xp": 70,
                "hints": [
                    "Volatility3 est le standard pour l'analyse mémoire.",
                    "vol3 -f dump.mem windows.pslist",
                ],
                "unlocks": [],
            },
        ],
    },
}

def get_all_missions_flat():
    """Retourne toutes les missions dans une liste plate."""
    flat = []
    for cat_id, cat_data in MISSIONS.items():
        for m in cat_data["missions"]:
            m["category"] = cat_id
            flat.append(m)
    return flat

def get_mission_by_id(mission_id):
    for cat_data in MISSIONS.values():
        for m in cat_data["missions"]:
            if m["id"] == mission_id:
                return m
    return None
