"""
Mode texte « vivant » : quand une mission sans vrai labo est réussie, on affiche
une sortie simulée réaliste de l'outil, au lieu de ne rien montrer.

Tout est factice et scripté (aucun réseau, aucun scan réel) : c'est purement
illustratif, pour que le joueur voie à quoi ressemble la sortie de l'outil.
"""
import re

GREEN = "\033[92m"; CYAN = "\033[96m"; YELLOW = "\033[93m"; DIM = "\033[2m"; RESET = "\033[0m"

IP_RE = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b")
URL_RE = re.compile(r"https?://[^\s'\"]+")
DOM_RE = re.compile(r"\b([a-z0-9][a-z0-9.-]*\.[a-z]{2,})\b", re.I)


def _target(cmd, default="10.10.10.5"):
    m = IP_RE.search(cmd)
    return m.group(1) if m else default


def _host(cmd, default="target.com"):
    u = URL_RE.search(cmd)
    if u:
        m = re.search(r"https?://([^/\s:'\"]+)", u.group(0))
        if m:
            return m.group(1)
    d = DOM_RE.search(re.sub(r"\.(sh|txt|py|conf|log|zip|bin)\b", "", cmd))
    return d.group(1) if d else default


def _box(title, body):
    return f"{DIM}┌─ simulation ─ {title}{RESET}\n{body}\n{DIM}└─ (sortie factice, aucun vrai réseau){RESET}"


# ── générateurs par outil ──────────────────────────────────────────────────
def _nmap(cmd):
    t = _target(cmd)
    return (f"Starting Nmap 7.95 ( https://nmap.org )\n"
            f"Nmap scan report for {t}\n"
            f"Host is up (0.012s latency).\n"
            f"PORT     STATE SERVICE     VERSION\n"
            f"22/tcp   open  ssh         OpenSSH 8.9p1\n"
            f"80/tcp   open  http        Apache httpd 2.4.52\n"
            f"445/tcp  open  microsoft-ds Samba smbd 4.15\n"
            f"3306/tcp open  mysql       MySQL 8.0.33\n"
            f"Nmap done: 1 IP address (1 host up) scanned in 6.84 seconds")


def _masscan(cmd):
    return ("Starting masscan 1.3.2\nDiscovered open port 80/tcp on 10.10.12.4\n"
            "Discovered open port 443/tcp on 10.10.9.18\nDiscovered open port 22/tcp on 10.10.3.7\n"
            "rate: 10.00-kpps, 100.00% done")


def _dirbust(cmd):
    h = _host(cmd, "target.com")
    base = f"http://{h}" if "://" not in cmd else URL_RE.search(cmd).group(0).rstrip("/")
    return (f"===============================================================\n"
            f"{base}/admin            (Status: 301) [Size: 312]\n"
            f"{base}/login            (Status: 200) [Size: 1024]\n"
            f"{base}/backup           (Status: 200) [Size: 88]\n"
            f"{base}/robots.txt       (Status: 200) [Size: 42]\n"
            f"{base}/config.php       (Status: 200) [Size: 0]\n"
            f"===============================================================")


def _nikto(cmd):
    h = _host(cmd)
    return (f"- Nikto v2.5.0\n+ Target Host: {h}\n+ Server: Apache/2.4.52\n"
            f"+ /admin/: Admin login page found.\n"
            f"+ Cookie PHPSESSID without HttpOnly flag.\n"
            f"+ OSVDB-3233: /icons/README: Apache default file found.")


def _whatweb(cmd):
    h = _host(cmd)
    return (f"http://{h} [200 OK] Apache[2.4.52], Country[RESERVED], HTTPServer[Apache/2.4.52], "
            f"PHP[7.4.3], WordPress[6.2], JQuery[3.6.0], IP[10.10.10.5]")


def _sqlmap(cmd):
    if "--dump" in cmd:
        return ("Database: shop\nTable: users\n[3 entries]\n"
                "+----+----------+------------------+\n| id | username | password         |\n"
                "+----+----------+------------------+\n| 1  | admin    | 5f4dcc3b5aa765d6 |\n"
                "| 2  | bob      | e10adc3949ba59ab |\n+----+----------+------------------+")
    if "--tables" in cmd:
        return ("Database: shop\n[3 tables]\n+-----------+\n| users     |\n| products  |\n| orders    |\n+-----------+")
    return ("[*] testing connection to the target URL\n"
            "[*] the back-end DBMS is MySQL\n[*] fetching database names\n"
            "available databases [3]:\n[*] information_schema\n[*] mysql\n[*] shop")


def _wpscan(cmd):
    return ("[+] WordPress version 6.2 identified\n"
            "[+] WPScan found 1 vulnerability\n"
            "[i] Plugin(s) Identified: contact-form-7 (outdated)\n"
            "[+] Enumerating users... admin, editor")


def _hydra(cmd):
    t = _target(cmd)
    return (f"Hydra v9.5 starting\n[DATA] attacking {t}\n"
            f"[22][ssh] host: {t}   login: admin   password: Summer2026!\n"
            f"1 of 1 target successfully completed, 1 valid password found")


def _hashcat(cmd):
    return ("hashcat (v6.2.6) starting\nSession..........: hashcat\nStatus...........: Cracked\n"
            "5f4dcc3b5aa765d61d8327deb882cf99:password\n"
            "e10adc3949ba59abbe56e057f20f883e:123456")


def _john(cmd):
    return ("Using default input encoding: UTF-8\nLoaded 2 password hashes\n"
            "Proceeding with wordlist:/usr/share/wordlists/rockyou.txt\n"
            "password         (user1)\nhunter2          (user2)\n2g 0:00:00:01 DONE")


def _hashid(cmd):
    return ("Analyzing '5f4dcc3b5aa765d61d8327deb882cf99'\n[+] MD5\n[+] NTLM")


def _dns(cmd):
    h = _host(cmd)
    return (f";; ANSWER SECTION:\n{h}.    300  IN  A   10.10.10.5\n"
            f"{h}.    300  IN  MX  10 mail.{h}.\n{h}.    300  IN  TXT \"v=spf1 include:_spf.{h} ~all\"")


def _whois(cmd):
    h = _host(cmd)
    return (f"Domain Name: {h.upper()}\nRegistrar: Example Registrar, Inc.\n"
            f"Creation Date: 2019-04-12\nName Server: NS1.{h.upper()}\nName Server: NS2.{h.upper()}")


def _msfvenom(cmd):
    return ("[-] No platform was selected, choosing Msf::Module::Platform::Linux\n"
            "Payload size: 74 bytes\nFinal size of elf file: 194 bytes\nSaved as: shell.elf")


def _searchsploit(cmd):
    return ("------------------------------------------ ---------------------------------\n"
            " Exploit Title                             |  Path\n"
            "------------------------------------------ ---------------------------------\n"
            " Apache 2.4.49 - Path Traversal (RCE)      | multiple/webapps/50383.sh\n"
            " vsftpd 2.3.4 - Backdoor Command Execution | unix/remote/17491.rb")


def _metasploit(cmd):
    return ("[*] Started reverse TCP handler on 10.10.14.3:4444\n"
            "[*] Sending stage (1017704 bytes)\n"
            "[*] Meterpreter session 1 opened\nmeterpreter > getuid\nServer username: root")


def _aircrack(cmd):
    return ("Reading packets...\n  CH  6 ][ Elapsed: 12 s\n"
            "BSSID              PWR  Beacons  ESSID\n"
            "AA:BB:CC:DD:EE:FF  -42      120  HomeWiFi\n"
            "[ WPA handshake: AA:BB:CC:DD:EE:FF ]\nKEY FOUND! [ motdepasse2026 ]")


def _cme(cmd):
    t = _target(cmd)
    return (f"SMB  {t}  445  DC01  [*] Windows Server 2019 (domain:CORP)\n"
            f"SMB  {t}  445  DC01  [+] CORP\\admin:Summer2026! (Pwn3d!)")


def _responder(cmd):
    return ("[+] Listening for events...\n[SMB] NTLMv2-SSP Hash captured from 10.10.10.42\n"
            "CORP\\jdoe::CORP:1122...:aef3... (hash enregistré dans Responder/logs)")


def _crypto(cmd):
    return ("[+] Décodage en cours...\n[+] Résultat : FLAG{simulation_crypto}")


def _proxychains(cmd):
    inner = re.sub(r"^\s*proxychains\d?\s+", "", cmd)
    return f"[proxychains] config: /etc/proxychains.conf\n[proxychains] DLL init\n$ {inner}\n...(trafic routé via le proxy)"


# ── table de correspondance (ordre = priorité) ─────────────────────────────
_RULES = [
    (r"\bmasscan\b", _masscan),
    (r"\bnmap\b", _nmap),
    (r"\b(gobuster|ffuf|dirb|feroxbuster|wfuzz|dirsearch)\b", _dirbust),
    (r"\bnikto\b", _nikto),
    (r"\b(whatweb|wappalyzer)\b", _whatweb),
    (r"\bsqlmap\b", _sqlmap),
    (r"\bwpscan\b", _wpscan),
    (r"\bhydra\b", _hydra),
    (r"\bhashcat\b", _hashcat),
    (r"\bjohn\b", _john),
    (r"\bhash(id|-identifier)\b", _hashid),
    (r"\b(dig|nslookup|host)\b", _dns),
    (r"\bwhois\b", _whois),
    (r"\bmsfvenom\b", _msfvenom),
    (r"\bsearchsploit\b", _searchsploit),
    (r"\b(msfconsole|metasploit|meterpreter|exploit/)\b", _metasploit),
    (r"\b(aircrack-ng|airodump-ng|aireplay-ng|airmon-ng)\b", _aircrack),
    (r"\b(crackmapexec|nxc|netexec)\b", _cme),
    (r"\bresponder\b", _responder),
    (r"\b(xor|rsa|vigenere|cipher|encode|magic|padding-oracle|ecb-detect)\b", _crypto),
    (r"\bproxychains\d?\b", _proxychains),
]


def simulated_output(cmd):
    """Renvoie une sortie simulée pour la commande, ou None si aucun outil connu."""
    low = cmd.lower()
    for pat, fn in _RULES:
        if re.search(pat, low):
            try:
                tool = re.search(pat, low).group(0)
                return _box(tool, fn(cmd))
            except Exception:
                return None
    return None
