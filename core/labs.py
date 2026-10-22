"""
Labos : les missions jouées dans le bac à sable (core/sandbox.py).

Pour chaque mission :
  cwd         dossier de départ (défaut : /home/hacker)
  setup       script lancé en `hacker` avant la mission
  setup_root  script lancé en root avant la mission
  background  script root lancé en tâche de fond (ex. un log qui grossit)
  timeout     durée max d'une commande en secondes (défaut : 10)
  checks      alternatives ; l'objectif est atteint si l'une d'elles est vraie :
                out      texte(s) présent(s) dans la sortie
                not_out  texte(s) absent(s) de la sortie
                re       regex trouvée dans la sortie (multiligne)
                lines    nombre exact de lignes non vides
                same_as  la sortie contient celle de cette commande
                test     ce script renvoie 0 (lancé dans le shell du joueur)
              sans `checks` : la commande doit simplement réussir (code 0)
  solution    une réponse correcte, utilisée par tests/test_labs.py

Dans tous les cas, la commande doit aussi être celle de la mission
(core/validate.py) : un `cat` qui affiche le flag ne valide pas une mission grep.
Les fichiers cités ici sont créés par lab/world.py.
"""

LABS = {
    # ── Navigation ───────────────────────────────────────────────────────
    "nav_01": {"checks": [{"out": "/home/hacker"}], "solution": "pwd"},
    "nav_02": {"checks": [{"out": "notes.txt"}], "solution": "ls"},
    "nav_03": {"checks": [{"out": ".secret", "re": r"^[-d]rw"}], "solution": "ls -la"},
    "nav_04": {"checks": [{"re": r"\s2\.4M\s"}], "solution": "ls -lh"},
    "nav_05": {"checks": [{"test": '[ "$PWD" = /var/log ]'}], "solution": "cd /var/log"},
    "nav_06": {"cwd": "/home/hacker/projet/src",
               "checks": [{"test": '[ "$PWD" = /home/hacker/projet ]'}], "solution": "cd .."},
    "nav_07": {"cwd": "/var/log",
               "checks": [{"test": '[ "$PWD" = "$HOME" ]'}], "solution": "cd ~"},
    "nav_08": {"checks": [{"out": ["crypto.py", "directories"]}], "solution": "tree projet"},
    "nav_09": {"checks": [{"out": "/opt/backup/.old/credentials.txt"}],
               "solution": "find / -name credentials.txt 2>/dev/null"},
    "nav_10": {"checks": [{"out": "/etc/nginx/sites-enabled", "not_out": "nginx.conf"}],
               "solution": "find /etc -type d"},
    "nav_11": {"checks": [{"out": "/usr/local/bin/backup-tool"}],
               "solution": "find / -perm -4000 2>/dev/null"},
    "nav_12": {"checks": [{"re": r"^/"}], "solution": "locate credentials"},

    # ── Fichiers ─────────────────────────────────────────────────────────
    "fil_01": {"checks": [{"out": "FLAG{premier_fichier_lu}"}], "solution": "cat note.txt"},
    "fil_02": {"checks": [{"re": r"^\s+\d+\t"}], "solution": "cat -n rapport.txt"},
    "fil_03": {"checks": [{"out": "ligne 10000"}], "solution": "less dump.txt"},
    "fil_04": {"checks": [{"lines": 20}], "solution": "head -n 20 logs/app.log"},
    "fil_05": {"checks": [{"out": "FLAG{fin_du_log_atteinte}", "not_out": "#0\n"}],
               "solution": "tail -n 5 logs/app.log"},
    "fil_06": {"background": "while :; do echo \"$(date '+%b %d %T') srv-target nginx[812]: "
                             "GET /admin/login 401 (LIVE)\" >> /var/log/syslog; sleep 1; done",
               "timeout": 6, "checks": [{"out": "(LIVE)"}], "solution": "tail -f /var/log/syslog"},
    "fil_07": {"solution": "touch test.txt"},
    "fil_08": {"solution": "mkdir loot"},
    "fil_09": {"checks": [{"test": "[ -d /tmp/pentest/loot/creds ]"}],
               "solution": "mkdir -p /tmp/pentest/loot/creds"},
    "fil_10": {"checks": [{"test": "find / -xdev -name '*.bak' -cnewer /run/hq/start 2>/dev/null | grep -q ."}],
               "solution": "cp /etc/passwd passwd.bak"},
    "fil_11": {"checks": [{"test": "find / -xdev -path /etc/nginx -prune -o -name nginx.conf "
                                   "-cnewer /run/hq/start -print 2>/dev/null | grep -q ."}],
               "solution": "cp -r /etc/nginx /tmp/nginx_bak"},
    "fil_12": {"checks": [{"test": "[ ! -e ~/suspicious.txt ] && find ~ /tmp -name found_creds.txt | grep -q ."}],
               "solution": "mv suspicious.txt found_creds.txt"},
    "fil_13": {"checks": [{"test": "[ ! -e ~/traces.log ]"}], "solution": "rm traces.log"},
    "fil_14": {"setup": "mkdir -p /tmp/pentest/loot/creds && echo x > /tmp/pentest/loot/creds/hash.txt",
               "checks": [{"test": "[ ! -e /tmp/pentest ]"}], "solution": "rm -rf /tmp/pentest/"},
    "fil_15": {"checks": [{"out": "ELF"}], "solution": "file suspicious.bin"},
    "fil_16": {"checks": [{"out": "Inode"}], "solution": "stat /etc/passwd"},
    "fil_17": {"checks": [{"same_as": "wc -l < /etc/passwd"}], "solution": "wc -l /etc/passwd"},
    "fil_18": {"checks": [{"out": ["PermitRootLogin no", "PermitRootLogin yes"]}],
               "solution": "diff config_v1.conf config_v2.conf"},
    "fil_19": {"checks": [{"test": "find ~ /tmp /usr/local/bin -maxdepth 2 -type l -lname '*python3*' "
                                   "-cnewer /run/hq/start | grep -q ."}],
               "solution": "ln -s /usr/local/bin/python3 /usr/local/bin/python"},
    "fil_20": {"checks": [{"re": r"\A\s*10\. FIN"}], "solution": "tac ordre.txt"},

    # ── Texte ────────────────────────────────────────────────────────────
    "txt_01": {"checks": [{"out": "FLAG{breach_localise}"}], "solution": "grep BREACH /var/log/syslog"},
    "txt_02": {"checks": [{"out": "FLAG{grep_recursif_payant}"}],
               "solution": "grep -r password /etc/ 2>/dev/null"},
    "txt_03": {"checks": [{"out": ["Admin", "ADMIN", "aDmIn"]}], "solution": "grep -i admin data/users.txt"},
    "txt_04": {"checks": [{"out": "PermitRootLogin yes", "not_out": "#"}],
               "solution": "grep -v '^#' /etc/ssh/sshd_config"},
    "txt_05": {"checks": [{"re": r"^\d+:.*error"}], "solution": "grep -n error logs/access.log"},
    "txt_06": {"checks": [{"out": ["root:", "admin:"], "not_out": "hacker:"}],
               "solution": "grep -E '^(root|admin)' /etc/passwd"},
    "txt_07": {"checks": [{"re": r"^37$"}], "solution": "grep -c failed /var/log/auth.log"},
    "txt_08": {"checks": [{"out": ["root", "hacker"], "not_out": ":"}], "solution": "cut -d: -f1 /etc/passwd"},
    "txt_09": {"checks": [{"same_as": "sort ~/data/domaines.txt"}], "solution": "sort data/domaines.txt"},
    "txt_10": {"checks": [{"same_as": "sort -n ~/data/ports.txt"}], "solution": "sort -n data/ports.txt"},
    "txt_11": {"checks": [{"same_as": "sort -u ~/data/ips.txt"}], "solution": "sort data/ips.txt | uniq"},
    "txt_12": {"checks": [{"re": r"\A\s*\d+ 185\.220\.101\.42\b"}],
               "solution": "awk '{print $1}' logs/access.log | sort | uniq -c | sort -rn | head"},
    "txt_13": {"checks": [{"out": "185.220.101.42", "not_out": "GET"}],
               "solution": "awk '{print $1}' logs/access.log"},
    "txt_14": {"checks": [{"out": "10.0.0.77", "not_out": "203.0.113.9"}],
               "solution": "awk '$9 == 200 {print $1}' logs/access.log"},
    "txt_15": {"checks": [{"out": "https://srv-target.corp", "not_out": "http://"},
                          {"test": "grep -q https:// ~/config/site.conf && ! grep -q http:// ~/config/site.conf"}],
               "solution": "sed 's/http/https/g' config/site.conf"},
    "txt_16": {"checks": [{"out": "debug=true", "not_out": ["#", "\n\n"]},
                          {"test": "! grep -qE '^(#|$)' ~/config/app.conf && grep -q debug ~/config/app.conf"}],
               "solution": "sed '/^#/d;/^$/d' config/app.conf"},
    "txt_17": {"checks": [{"re": r"\A[^a-z]*[A-Z][^a-z]*\Z"}], "solution": "echo 'hello' | tr 'a-z' 'A-Z'"},
    "txt_18": {"checks": [{"test": "! ls ~/tmpfiles/*.tmp >/dev/null 2>&1"}],
               "solution": "cat a_supprimer.txt | xargs rm"},
    "txt_19": {"checks": [{"test": "find ~ /tmp -maxdepth 2 -type f -size +0 -cnewer /run/hq/start | grep -q ."}],
               "solution": "ls | tee liste.txt"},
    "txt_20": {"checks": [{"out": "FLAG{strings_revele_tout}"}], "solution": "strings binaire | grep -i pass"},
    "txt_21": {"checks": [{"re": r"^00000000: "}], "solution": "xxd fichier.bin | head -20"},

    # ── Permissions ──────────────────────────────────────────────────────
    "perm_01": {"checks": [{"test": "[ -x ~/exploit.sh ]"}], "solution": "chmod +x exploit.sh"},
    "perm_02": {"checks": [{"test": '[ "$(stat -c %a ~/id_rsa)" = 600 ]'}], "solution": "chmod 600 id_rsa"},
    "perm_03": {"checks": [{"test": '[ "$(stat -c %a ~/world_me.txt)" = 777 ]'}],
                "solution": "chmod 777 world_me.txt"},
    "perm_06": {"checks": [{"re": r"^hacker$"}], "solution": "whoami"},
    "perm_07": {"checks": [{"out": "uid=1000", "re": r"gid=\d+"}], "solution": "id"},
    "perm_13": {"checks": [{"re": r"^0?\d{3}$"}], "solution": "umask"},

    # ── Processus ────────────────────────────────────────────────────────
    "proc_01": {"checks": [{"out": ["PID", "COMMAND"]}], "solution": "ps aux"},
    "proc_02": {"background": "exec -a nginx sleep 100000",
                "checks": [{"out": "nginx"}], "solution": "ps aux | grep nginx"},
    # nohup.out n'apparaît qu'avec un vrai terminal ; ici on vérifie que le processus tourne en fond
    "proc_08": {"checks": [{"test": "sleep 0.4; [ -f ~/nohup.out ] || pgrep -u hacker -x sleep >/dev/null"}],
                "solution": "nohup sleep 300 &"},
    "proc_13": {"checks": [{"out": "Linux"}], "solution": "uname -a"},
    "proc_14": {"checks": [{"out": "load average"}], "solution": "uptime"},
    "proc_15": {"checks": [{"out": "sleep"}], "solution": "pstree"},

    # ── Archives ─────────────────────────────────────────────────────────
    "arc_01": {"checks": [{"test": "find ~ /tmp -maxdepth 2 -name '*.tar.gz' -cnewer /run/hq/start "
                                   "! -name exploit.tar.gz | grep -q ."}],
               "solution": "tar -czf nginx.tar.gz /etc/nginx"},
    "arc_02": {"checks": [{"test": "find ~ /tmp -name secret.txt -cnewer /run/hq/start | grep -q ."}],
               "solution": "tar -xzf exploit.tar.gz"},
    "arc_03": {"checks": [{"out": "secret.txt", "not_out": "FLAG"}], "solution": "tar -tzf exploit.tar.gz"},
    "arc_04": {"checks": [{"test": "[ -f ~/gros.log.gz ] && [ ! -f ~/gros.log ]"}], "solution": "gzip gros.log"},
    "arc_05": {"checks": [{"test": "[ -f ~/access.log.saved ] && [ ! -f ~/access.log.saved.gz ]"}],
               "solution": "gunzip access.log.saved.gz"},
    "arc_06": {"checks": [{"test": "find ~ /tmp -maxdepth 2 -name '*.zip' -cnewer /run/hq/start | grep -q ."}],
               "solution": "zip loot.zip notes.txt note.txt"},
    "arc_07": {"checks": [{"test": "find ~ /tmp -maxdepth 2 -name '*.7z' -cnewer /run/hq/start | grep -q ."}],
               "solution": "7z a loot.7z notes.txt"},

    # ── Système ──────────────────────────────────────────────────────────
    "sys_01": {"checks": [{"re": r"%|Avail|Mont"}], "solution": "df -h"},
    "sys_02": {"checks": [{"re": r"\d"}], "solution": "du -sh /var/data"},
    "sys_03": {"checks": [{"out": "Mem"}], "solution": "free -h"},
    "sys_04": {"env": {"DB_PASSWORD": "FLAG{credentials_dans_env}"},
               "checks": [{"out": "FLAG{credentials_dans_env}"}], "solution": "env | grep -i pass"},
    "sys_08": {"checks": [{"out": "/opt/backup/run.sh"}], "solution": "crontab -l"},
    "sys_13": {"checks": [{"out": "root:x:0:0"}], "solution": "cat /etc/passwd"},
    "sys_14": {"checks": [{"out": "FLAG_hash_a_cracker"}], "solution": "cat /etc/shadow.bak"},

    # ── Scripting ────────────────────────────────────────────────────────
    "scr_01": {"checks": [{"re": r"\S"}], "solution": "TARGET=10.10.10.5 && echo $TARGET"},
    "scr_02": {"checks": [{"test": "find ~ /tmp -maxdepth 2 -type f -cnewer /run/hq/start "
                                   "! -name nohup.out | grep -q ."}],
               "solution": "echo resultat > scan.txt"},
    "scr_03": {"checks": [{"not_out": "Permission denied", "re": r"\S"}],
               "solution": "find / -name secret 2>/dev/null"},
    "scr_04": {"checks": [{"re": r"\S"}], "solution": 'if [ -f /etc/passwd ]; then echo "existe"; fi'},
    "scr_05": {"checks": [{"lines": 3}], "solution": "for ip in 1 2 3; do echo 10.0.0.$ip; done"},
    "scr_06": {"checks": [{"re": r"\S"}], "solution": "i=0; while [ $i -lt 3 ]; do echo $i; i=$((i+1)); done"},
    "scr_07": {"checks": [{"re": r"\S"}], "solution": 'function salut() { echo "bonjour $1"; }; salut monde'},
    "scr_08": {"checks": [{"re": r"\S"}], "solution": 'set -- 10.0.0.5 80; echo "cible $1 port $2"'},
    "scr_09": {"checks": [{"re": r"^\d+$"}], "solution": "false; echo $?"},
    "scr_10": {"checks": [{"out": "ligne1"}], "solution": "cat <<EOF\nligne1\nligne2\nEOF"},
    "scr_11": {"checks": [{"re": r"\S"}],
               "solution": "awk '{print $1}' logs/access.log | sort | uniq -c | sort -rn | head -5"},
    "scr_13": {"checks": [{"out": "analyse de"}], "solution": "chmod +x scan.sh && ./scan.sh 10.0.0.5"},

    # ── Avancé ───────────────────────────────────────────────────────────
    "adv_03": {"checks": [{"re": r"[A-Za-z0-9+/]{8,}={0,2}"}], "solution": "echo 'payload' | base64"},
    "adv_04": {"checks": [{"re": r"^[0-9a-f]{32,}"}], "solution": "md5sum a_hasher.bin"},
    "adv_05": {"checks": [{"re": r"\S"}], "solution": "openssl rand -hex 16"},
    "adv_08": {"checks": [{"re": r"^\d"}], "solution": "echo '1500000 / 1024 / 1024' | bc"},
    "adv_11": {"checks": [{"test": "find /tmp -path '*creds.txt' -cnewer /run/hq/start | grep -q ."}],
               "solution": "rsync -av exfil/ /tmp/exfil_copie/"},
}

# Indice contextuel affiché au début de chaque labo (où chercher)
WHERE = {
    "fil_02": "rapport.txt", "fil_03": "dump.txt (10 000 lignes)", "fil_04": "logs/app.log",
    "fil_05": "logs/app.log", "fil_12": "suspicious.txt", "fil_13": "traces.log",
    "fil_15": "suspicious.bin", "fil_18": "config_v1.conf et config_v2.conf", "fil_20": "ordre.txt",
    "txt_03": "data/users.txt", "txt_05": "logs/access.log", "txt_09": "data/domaines.txt",
    "txt_10": "data/ports.txt", "txt_11": "data/ips.txt", "txt_12": "logs/access.log",
    "txt_13": "logs/access.log", "txt_14": "logs/access.log", "txt_15": "config/site.conf",
    "txt_16": "config/app.conf", "txt_18": "a_supprimer.txt", "txt_20": "binaire", "txt_21": "fichier.bin",
    "nav_08": "projet/",
    "perm_01": "exploit.sh", "perm_02": "id_rsa", "perm_03": "world_me.txt",
    "arc_02": "exploit.tar.gz", "arc_03": "exploit.tar.gz", "arc_04": "gros.log",
    "arc_05": "access.log.saved.gz", "sys_02": "/var/data", "sys_08": "crontab de hacker",
    "sys_14": "/etc/shadow.bak", "scr_05": "cibles.txt", "scr_13": "scan.sh",
    "adv_04": "a_hasher.bin", "adv_11": "exfil/",
}
