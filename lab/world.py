"""
Construit le monde du labo (exécuté une seule fois, en root, pendant `docker build`).

Le décor : srv-target, un serveur web compromis. Le joueur est l'utilisateur
`hacker` et fouille le système. Chaque fichier sert à au moins une mission
(voir core/labs.py) : si tu modifies une valeur ici, vérifie la mission associée.
"""
import gzip
import os
import random
import shutil
import struct
import subprocess
import zipfile
import zlib

random.seed(1337)  # même monde à chaque construction
H = "/home/hacker"


# ── petits générateurs de fichiers (sans dépendance : utiles pour la forensics) ──
def make_png(w, h, rgb=(70, 130, 180)):
    """Un PNG RGB valide (signature + IHDR/IDAT/IEND), carvable par foremost."""
    def chunk(typ, data):
        body = typ + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def make_bmp(w, h):
    """Un BMP 24 bits bruité : support de couverture pour steghide."""
    rowsize = (w * 3 + 3) & ~3
    pixels = bytearray()
    for _ in range(h):
        pixels += random.randbytes(w * 3) + b"\x00" * (rowsize - w * 3)
    datasize = rowsize * h
    hdr = b"BM" + struct.pack("<IHHI", 54 + datasize, 0, 0, 54)
    dib = struct.pack("<IiiHHIIiiII", 40, w, h, 1, 24, 0, datasize, 2835, 2835, 0, 0)
    return hdr + dib + bytes(pixels)


def make_dns_pcap(qname):
    """Une capture pcap d'une seule requête DNS (lisible par tshark, sans réseau)."""
    labels = b"".join(bytes([len(p)]) + p.encode() for p in qname.split(".")) + b"\x00"
    dns = struct.pack(">HHHHHH", 0x1337, 0x0100, 1, 0, 0, 0) + labels + struct.pack(">HH", 1, 1)
    udp = struct.pack(">HHHH", 40000, 53, 8 + len(dns), 0) + dns
    ip = struct.pack(">BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), 0x1234, 0, 64, 17, 0,
                     bytes([10, 0, 0, 77]), bytes([8, 8, 8, 8]))
    eth = b"\x52\x54\x00\x12\x34\x56\x52\x54\x00\x65\x43\x21\x08\x00"
    pkt = eth + ip + udp
    gheader = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
    pheader = struct.pack("<IIII", 0, 0, len(pkt), len(pkt))
    return gheader + pheader + pkt


def make_http_pcap(request_line, host="srv-target.corp"):
    """Une capture d'une seule requête HTTP (un segment TCP vers le port 80).
    tshark -r la dissèque en HTTP : la ligne de requête (avec l'URI) apparaît."""
    payload = (f"{request_line}\r\nHost: {host}\r\n"
               "User-Agent: curl/8.0\r\nAccept: */*\r\n\r\n").encode()
    tcp = struct.pack(">HHIIBBHHH", 44000, 80, 1000, 0, 0x50, 0x18, 64240, 0, 0) + payload
    ip = struct.pack(">BBHHHBBH4s4s", 0x45, 0, 20 + len(tcp), 0x2a2a, 0x4000, 64, 6, 0,
                     bytes([10, 0, 0, 77]), bytes([10, 10, 10, 5]))
    eth = b"\x52\x54\x00\x12\x34\x56\x52\x54\x00\x65\x43\x21\x08\x00"
    pkt = eth + ip + tcp
    gheader = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
    pheader = struct.pack("<IIII", 0, 0, len(pkt), len(pkt))
    return gheader + pheader + pkt


def sh(*cmd):
    subprocess.run(cmd, check=True)


def write(path, content, mode=0o644):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if isinstance(content, bytes) else "w") as f:
        f.write(content)
    os.chmod(path, mode)


def lines(items):
    return "\n".join(items) + "\n"


# ── Utilisateurs ─────────────────────────────────────────────────────────
sh("useradd", "-m", "-s", "/bin/bash", "-u", "1000", "hacker")
sh("useradd", "-M", "-s", "/bin/bash", "admin")          # txt_06 : ^(root|admin)
os.remove("/usr/local/bin/python")                       # fil_19 : ln -s ... python
write("/etc/hostname", "srv-target\n")

# ── Home : navigation ────────────────────────────────────────────────────
write(f"{H}/notes.txt", lines([
    "Notes d'intrusion — srv-target",
    "- accès initial via un mot de passe faible",
    "- regarder /var/log, /etc et /opt",
    "- des fichiers cachés traînent dans le home",
]))
write(f"{H}/.secret", "FLAG{fichiers_caches_reveles}\n")                         # nav_03
write(f"{H}/dump_memoire.bin", random.randbytes(2_500_000))                      # nav_04 : 2.4M
write(f"{H}/projet/README.md", "# Projet interne\n")
write(f"{H}/projet/src/main.py", "print('hello')\n")
write(f"{H}/projet/src/utils/crypto.py", "KEY = 'changeme'\n")
write(f"{H}/projet/docs/plan.txt", "Migration prévue en décembre.\n")

# ── Home : fichiers ──────────────────────────────────────────────────────
write(f"{H}/note.txt", lines([
    "Si tu lis ceci, tu sais utiliser cat.",
    "FLAG{premier_fichier_lu}",
]))                                                                               # fil_01
write(f"{H}/rapport.txt", lines(f"Point {i} du rapport d'audit" for i in range(1, 16)))  # fil_02
write(f"{H}/dump.txt", lines(f"ligne {i} — entrée de journal" for i in range(1, 10_001)))  # fil_03
app_log = [f"2026-10-21 08:{i // 60:02d}:{i % 60:02d} INFO requête traitée #{i}" for i in range(300)]
app_log.append("2026-10-21 13:00:00 CRIT dernière entrée : FLAG{fin_du_log_atteinte}")
write(f"{H}/logs/app.log", lines(app_log))                                        # fil_04, fil_05
write(f"{H}/suspicious.txt", "admin:Winter2026!\n")                               # fil_12
write(f"{H}/traces.log", "connexion depuis 185.220.101.42\n")                     # fil_13
shutil.copy("/usr/bin/whoami", f"{H}/suspicious.bin")                             # fil_15 : ELF
write(f"{H}/config_v1.conf", lines(["Port 22", "PermitRootLogin no", "PasswordAuthentication no", "MaxAuthTries 3"]))
write(f"{H}/config_v2.conf", lines(["Port 22", "PermitRootLogin yes", "PasswordAuthentication no", "MaxAuthTries 10"]))  # fil_18
write(f"{H}/ordre.txt", lines([f"{i}. étape {i}" for i in range(1, 10)] + ["10. FIN — lu à l'envers, je suis en premier"]))  # fil_20

# ── Home : texte ─────────────────────────────────────────────────────────
write(f"{H}/data/users.txt", lines([
    "alice user", "bob user", "Admin principal", "carol user",
    "ADMIN sauvegarde", "dave user", "aDmIn caché", "eve user",
]))                                                                               # txt_03
domaines = ["zeta.corp", "alpha.corp", "mail.corp", "vpn.corp", "dev.corp", "beta.corp", "intranet.corp"]
write(f"{H}/data/domaines.txt", lines(domaines))                                  # txt_09
write(f"{H}/data/ports.txt", lines(["8080", "22", "443", "3306", "80", "21", "8443", "25"]))  # txt_10
ips = ["10.0.0.5", "10.0.0.9", "192.168.1.20", "10.0.0.5", "172.16.0.3", "10.0.0.9", "10.0.0.5"]
write(f"{H}/data/ips.txt", lines(ips))                                            # txt_11

# access.log au format Apache : $1 = IP, $9 = code HTTP
#   185.220.101.42 : l'IP la plus fréquente (txt_12)
#   10.0.0.77      : uniquement des 200 (txt_14)
#   203.0.113.9    : uniquement des 404 (txt_14)
paths = ["/", "/index.php", "/login", "/admin", "/api/users", "/api/error", "/static/app.js"]
access = []
for i in range(400):
    roll = random.random()
    if roll < 0.35:
        ip, code = "185.220.101.42", random.choice([200, 401, 403])
    elif roll < 0.45:
        ip, code = "10.0.0.77", 200
    elif roll < 0.52:
        ip, code = "203.0.113.9", 404
    else:
        ip, code = f"192.168.1.{random.randint(2, 60)}", random.choice([200, 200, 302, 500])
    path = random.choice(paths)
    access.append(f'{ip} - - [21/Oct/2026:10:{i // 60:02d}:{i % 60:02d} +0100] "GET {path} HTTP/1.1" {code} {random.randint(200, 9000)}')
write(f"{H}/logs/access.log", lines(access))                                      # txt_05, 12, 13, 14

write(f"{H}/config/site.conf", lines([
    "url=http://srv-target.corp",
    "api=http://api.srv-target.corp/v1",
    "cdn=http://cdn.srv-target.corp",
]))                                                                               # txt_15
write(f"{H}/config/app.conf", lines([
    "# Configuration de l'application", "", "port=8080", "# debug activé en prod (!)",
    "debug=true", "", "", "# base de données", "db_host=127.0.0.1",
]))                                                                               # txt_16
for n in range(1, 6):
    write(f"{H}/tmpfiles/temp{n}.tmp", "x\n")
write(f"{H}/a_supprimer.txt", lines(f"tmpfiles/temp{n}.tmp" for n in range(1, 6)))  # txt_18
with open("/usr/bin/true", "rb") as f:
    binaire = f.read()
write(f"{H}/binaire", binaire + b"\x00\x00admin_password=FLAG{strings_revele_tout}\x00\x00", 0o755)  # txt_20
write(f"{H}/fichier.bin", b"\x7fHQ\x01" + bytes(range(32)) + b"FLAG{hexdump}\n")  # txt_21

# ── Système ──────────────────────────────────────────────────────────────
write("/opt/backup/.old/credentials.txt", "root:FLAG{find_fouille_partout}\n")      # nav_09
shutil.copy("/usr/bin/id", "/usr/local/bin/backup-tool")
os.chmod("/usr/local/bin/backup-tool", 0o4755)                                     # nav_11 : SUID
write("/etc/nginx/nginx.conf", "user www-data;\nworker_processes auto;\n")
write("/etc/nginx/sites-enabled/default", "server { listen 80; root /var/www/html; }\n")  # fil_11
write("/etc/app/db.conf", "host=127.0.0.1\nuser=app\npassword=FLAG{grep_recursif_payant}\n")  # txt_02
write("/etc/ssh/sshd_config", lines([
    "# Configuration SSH de srv-target", "#Port 22", "Port 2222",
    "# Ne jamais laisser root se connecter !", "PermitRootLogin yes",
    "#PasswordAuthentication no", "PasswordAuthentication yes",
]))                                                                               # txt_04

syslog = [f"Oct 21 0{i % 10}:{i % 60:02d}:{(i * 7) % 60:02d} srv-target cron[{1000 + i}]: job #{i} terminé" for i in range(3000)]
syslog[1874] = "Oct 21 03:14:15 srv-target kernel: BREACH detected — exfiltration vers 185.220.101.42 FLAG{breach_localise}"
write("/var/log/syslog", lines(syslog))                                          # txt_01, fil_06
auth = []
for i in range(120):
    if i % 3 == 0 and len([a for a in auth if "failed" in a]) < 37:
        auth.append(f"Oct 21 04:{i % 60:02d}:00 srv-target sshd[{2000 + i}]: authentication failed for root from 185.220.101.42")
    else:
        auth.append(f"Oct 21 04:{i % 60:02d}:00 srv-target sshd[{2000 + i}]: session opened for user hacker")
write("/var/log/auth.log", lines(auth))                                          # txt_07 : 37 « failed »
assert sum("failed" in a for a in auth) == 37

# ── Permissions ──────────────────────────────────────────────────────────
write(f"{H}/exploit.sh", "#!/bin/bash\necho 'exploit lancé'\n", 0o644)             # perm_01 : chmod +x
write(f"{H}/id_rsa", "-----BEGIN OPENSSH PRIVATE KEY-----\nFLAG{cle_privee}\n"
                     "-----END OPENSSH PRIVATE KEY-----\n", 0o644)                  # perm_02 : chmod 600
write(f"{H}/world_me.txt", "fichier aux permissions trop ouvertes\n", 0o644)       # perm_03 : chmod 777

# copie lisible de /etc/shadow pour la mission (dans la vraie vie, il ne l'est jamais)
write("/etc/shadow.bak", "root:$6$abc$FLAG_hash_a_cracker:19000:0:99999:7:::\n"
                         "hacker:$6$xyz$autre_hash:19000:0:99999:7:::\n", 0o644)    # sys_14
write("/opt/secret", "donnée sensible oubliée par l'admin\n")                      # scr_03 : cible de find

# ── Archives ─────────────────────────────────────────────────────────────
os.makedirs(f"{H}/arch", exist_ok=True)
write(f"{H}/arch/secret.txt", "FLAG{archive_extraite}\n")
write(f"{H}/arch/data.csv", "id,valeur\n1,42\n2,1337\n")
subprocess.run(["tar", "-czf", f"{H}/exploit.tar.gz", "-C", f"{H}/arch", "."], check=True)  # arc_02, arc_03
write(f"{H}/gros.log", lines(f"entrée de log numéro {i}" for i in range(500)))     # arc_04 : gzip
write(f"{H}/access.log.saved", lines(f"hit {i}" for i in range(300)))
subprocess.run(["gzip", f"{H}/access.log.saved"], check=True)                      # arc_05 : gunzip -> access.log.saved.gz

# ── Système ──────────────────────────────────────────────────────────────
os.makedirs("/var/data", exist_ok=True)
write("/var/data/gros_fichier.bin", random.randbytes(1_500_000))                   # sys_02 : du
# crontab de hacker (une tâche suspecte) pour sys_08 — hacker doit pouvoir la lire
sh("usermod", "-aG", "crontab", "hacker")
write("/tmp/hacker.cron", "# tâche planifiée du serveur\n*/5 * * * * /opt/backup/run.sh\n")
sh("su", "hacker", "-c", "crontab /tmp/hacker.cron")
os.remove("/tmp/hacker.cron")

# ── Scripting ────────────────────────────────────────────────────────────
write(f"{H}/scan.sh", "#!/bin/bash\necho \"analyse de $1 en cours...\"\n", 0o644)  # scr_13 : chmod +x && lancer
write(f"{H}/cibles.txt", lines(["10.0.0.1", "10.0.0.2", "10.0.0.3"]))              # scr_05 : for

# ── Avancé ───────────────────────────────────────────────────────────────
write(f"{H}/a_hasher.bin", b"contenu binaire a verifier\n")                        # adv_04 : md5sum/sha256sum
os.makedirs(f"{H}/exfil", exist_ok=True)
write(f"{H}/exfil/creds.txt", "admin:FLAG{loot_synchronise}\n")                     # adv_11 : rsync (dossier exfil, pas loot qui sert à fil_08)

# ── Reverse engineering ────────────────────────────────────────────────────
os.makedirs(f"{H}/reverse", exist_ok=True)
shutil.copy("/opt/crackme", f"{H}/reverse/crackme")                                # rev_01..05
os.chmod(f"{H}/reverse/crackme", 0o755)

# ── Post-exploitation ──────────────────────────────────────────────────────
# postex_03 : SUID → backup-tool (déjà planté pour nav_11)
# postex_04 : crontab → crontab de hacker (déjà planté pour sys_08)
# postex_05 : credentials dans l'environnement → via la variable d'env du labo

# ── Forensics ────────────────────────────────────────────────────────────
os.makedirs(f"{H}/forensics", exist_ok=True)
F = f"{H}/forensics"

# for_01 : exiftool — métadonnées cachées dans une image
write(f"{F}/photo.png", make_png(64, 64))
subprocess.run(["exiftool", "-overwrite_original", "-Artist=admin_pirate",
                "-Comment=FLAG{metadonnees_exif}", f"{F}/photo.png"],
               check=True, stdout=subprocess.DEVNULL)

# for_02 : binwalk — fichiers embarqués (un ZIP caché à la fin d'une image)
buf = make_png(32, 32) + random.randbytes(200)
zbuf = f"{F}/_hidden.zip"
with zipfile.ZipFile(zbuf, "w") as z:
    z.writestr("config_cache.txt", "FLAG{fichier_embarque}\n")
with open(zbuf, "rb") as z:
    buf += z.read()
os.remove(zbuf)
buf += gzip.compress(b"configuration secrete du firmware\n")
write(f"{F}/firmware.bin", buf)

# for_03 : strings — chaîne lisible dans un binaire
with open("/usr/bin/true", "rb") as f:
    write(f"{F}/malware.bin", f.read() + b"\x00C2_SERVER=185.220.101.42\x00"
                              b"PASSWORD=FLAG{strings_dans_malware}\x00", 0o755)

# for_05 : steghide — données cachées dans une image (phrase : hackquest)
write(f"{F}/message.txt", "FLAG{steghide_extrait}\n")
write(f"{F}/secret.bmp", make_bmp(200, 200))
subprocess.run(["steghide", "embed", "-cf", f"{F}/secret.bmp", "-ef", f"{F}/message.txt",
                "-p", "hackquest", "-q"], check=True)
os.remove(f"{F}/message.txt")                                                      # seul le .bmp reste

# for_06 : foremost — un PNG noyé dans une image disque, à récupérer
write(f"{F}/disk.img", random.randbytes(100_000) + make_png(80, 80)
                       + random.randbytes(50_000))

# for_07 : tshark — une requête DNS qui exfiltre un flag
write(f"{F}/capture.pcap", make_dns_pcap("FLAG-exfiltration.evil.corp"))

# for_08 : tshark — des credentials en clair dans une requête HTTP GET
write(f"{F}/capture_http.pcap",
      make_http_pcap("GET /login?user=admin&password=FLAG{http_creds_captures} HTTP/1.1"))

# for_12 : yara — règle de détection + fichier suspect
write(f"{F}/rules.yar", 'rule Backdoor_Detectee {\n'
                        '  strings:\n    $a = "backdoor_shell_2026"\n'
                        '  condition:\n    $a\n}\n')
write(f"{F}/suspect.exe", "programme anodin en apparence...\n"
                          "backdoor_shell_2026 FLAG{yara_a_matche}\n")

# for_13 : entropy — wrapper maison (pas d'outil standard « entropy »)
write("/usr/local/bin/entropy", "#!/usr/bin/env python3\n"
      "import sys, math, collections\n"
      "for f in sys.argv[1:]:\n"
      "    d = open(f, 'rb').read()\n"
      "    if not d:\n        print(f'{f}: 0.00 bits/octet'); continue\n"
      "    n = len(d); c = collections.Counter(d)\n"
      "    e = -sum((v/n) * math.log2(v/n) for v in c.values())\n"
      "    print(f'{f}: {e:.2f} bits/octet')\n", 0o755)
write(f"{F}/encrypted.bin", random.randbytes(50_000))                              # entropie ~8

# ══════════════════════════════════════════════════════════════════════════
#  Services réseau locaux (127.0.0.1) : démarrés le temps d'une mission.
#  Le conteneur reste sans réseau ; tout se passe en boucle locale.
# ══════════════════════════════════════════════════════════════════════════
os.makedirs("/opt/hq", exist_ok=True)

# ── Mini-site web volontairement vulnérable (simulation pédagogique) ──────
#   · plusieurs chemins « cachés » → énumération (gobuster/ffuf/dirb)
#   · un faux login contournable → SQLi manuelle via curl
#   · un en-tête Server identifiable → reconnaissance
write("/opt/hq/web.py", r'''#!/usr/bin/env python3
"""Serveur d'entraînement HackQuest — 100% local, aucune vraie base de données.
Les « failles » sont scriptées pour l'apprentissage : rien n'est réellement exploitable."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

PAGES = {
    "/": "<h1>srv-target</h1><p>Portail interne. Voir /robots.txt</p>",
    "/robots.txt": "User-agent: *\nDisallow: /admin\nDisallow: /backup\nDisallow: /secret",
    "/admin": "<h1>Zone admin</h1><form action=/login><input name=user><input name=password></form>",
    "/backup": "<h1>Sauvegardes</h1><a href=/backup/dump.sql>dump.sql</a>",
    "/config.php": "<!-- TODO: retirer les identifiants de debug -->",
    "/secret": "<h1>Zone secrete</h1>FLAG{repertoire_cache_trouve}",
}

class H(BaseHTTPRequestHandler):
    server_version = "Apache/2.4.52"
    sys_version = "(Debian)"
    def log_message(self, *a): pass
    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("X-Powered-By", "PHP/7.4.3")
        self.end_headers()
        self.wfile.write(body.encode())
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/login":
            q = parse_qs(u.query)
            user = (q.get("user") or [""])[0]
            pw = (q.get("password") or q.get("pass") or [""])[0]
            inj = "' or '1'='1"
            if inj in user.lower() or inj in pw.lower() or "or 1=1" in (user + pw).lower():
                return self._send(200, "Authentification contournee ! FLAG{sqli_authentification_contournee}")
            return self._send(403, "Identifiants invalides.")
        if u.path in PAGES:
            return self._send(200, PAGES[u.path])
        self._send(404, "Not Found")
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        self._send(200, "Requete POST recue. FLAG{post_envoye}")

HTTPServer(("127.0.0.1", 80), H).serve_forever()
''', 0o755)

# ── Liste de mots pour l'énumération et le cassage (petite = cassage rapide) ──
WORDS = ["admin", "login", "backup", "secret", "config.php", "robots.txt", "index",
         "images", "uploads", "test", "old", "dev", "api",
         "password", "letmein", "hunter2", "azerty", "dragon", "qwerty",
         "root", "toor", "admin123", "Winter2026!", "P4ssw0rd"]
write("/opt/hq/wordlist.txt", lines(WORDS))

# ── Lanceur de services (appelé en root au début des missions concernées) ──
write("/opt/hq/svc", r'''#!/bin/bash
# usage: svc web ssh dns   — démarre les services demandés et attend qu'ils répondent
wait_port() { for _ in $(seq 1 50); do (echo >/dev/tcp/127.0.0.1/$1) 2>/dev/null && return; sleep 0.1; done; }
for s in "$@"; do case "$s" in
  web) pgrep -f /opt/hq/web.py >/dev/null || nohup python3 /opt/hq/web.py >/var/log/hqweb.log 2>&1 &
       wait_port 80 ;;
  ssh) mkdir -p /run/sshd
       pgrep -f "sshd.*Port=22" >/dev/null || /usr/sbin/sshd \
         -o Port=22 -o ListenAddress=127.0.0.1 \
         -o PasswordAuthentication=no -o PubkeyAuthentication=yes \
         -o UsePAM=no -o StrictModes=no
       wait_port 22 ;;
  dns) pgrep -x dnsmasq >/dev/null || dnsmasq --user=root --listen-address=127.0.0.1 --bind-interfaces \
         --no-resolv --no-hosts \
         --address=/srv-target.corp/10.10.10.5 \
         --address=/mail.srv-target.corp/10.10.10.9 \
         --address=/vpn.srv-target.corp/10.10.10.20
       echo "nameserver 127.0.0.1" > /etc/resolv.conf ;;
esac; done
''', 0o755)

# ── sshd : login par clé de hacker vers localhost (net_19/20) ──────────────
write("/etc/ssh/sshd_config.d/hq.conf", lines([
    "Port 22", "ListenAddress 127.0.0.1",
    "PermitRootLogin no", "PasswordAuthentication no", "PubkeyAuthentication yes",
    "UsePAM no",
]))
# le compte hacker est créé verrouillé (pas de mot de passe) : on le déverrouille
# pour que l'authentification par clé fonctionne (l'auth par mot de passe reste coupée)
sh("bash", "-c", "echo 'hacker:hackquest2026' | chpasswd")
os.makedirs(f"{H}/.ssh", exist_ok=True)
sh("ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", f"{H}/.ssh/id_ed25519")
with open(f"{H}/.ssh/id_ed25519.pub") as f:
    pub = f.read()
write(f"{H}/.ssh/authorized_keys", pub)
write(f"{H}/.ssh/config", lines([
    "Host srv-target localhost 127.0.0.1",
    "    HostName 127.0.0.1",
    "    User hacker",
    "    StrictHostKeyChecking no",
    "    UserKnownHostsFile /dev/null",
    "    LogLevel ERROR",
]))

# ── Artefacts à casser (mots de passe) — volontairement faibles et locaux ──
os.makedirs(f"{H}/crack", exist_ok=True)
# pass_01 : identifier un hash — MD5 de "password"
write(f"{H}/crack/hash.txt", "5f4dcc3b5aa765d61d8327deb882cf99\n")
# pass_07 : john sur des hash md5crypt ($1$) dont le clair est dans la wordlist
#   (la version « core » de john en dépôt ne gère pas raw-md5, mais gère md5crypt)
_targets = ["letmein", "hunter2", "dragon"]
_hashes = [subprocess.run(["openssl", "passwd", "-1", w], capture_output=True, text=True).stdout.strip()
           for w in _targets]
write(f"{H}/crack/hashes.txt", lines(f"user{i}:{h}" for i, h in enumerate(_hashes)))
write(f"{H}/crack/wordlist.txt", lines(WORDS))
# pass_08 : archive ZIP protégée (mot de passe « letmein », présent dans la wordlist)
_zc = f"{H}/crack/_flag.txt"
write(_zc, "FLAG{zip_casse_au_dictionnaire}\n")
subprocess.run(["zip", "-q", "-j", "--password", "letmein", f"{H}/crack/secret.zip", _zc], check=True)
os.remove(_zc)

sh("chown", "-R", "hacker:hacker", H)
sh("chown", "hacker:hacker", "/usr/local/bin")                                     # fil_19 : ln -s dans /usr/local/bin
# perms SSH strictes (sinon le client/daemon refusent les clés)
os.chmod(f"{H}/.ssh", 0o700)
os.chmod(f"{H}/.ssh/id_ed25519", 0o600)
os.chmod(f"{H}/.ssh/authorized_keys", 0o600)
