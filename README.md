# HackQuest 🎮

Apprends Linux et la cybersécurité en jouant dans le terminal.

## Installation rapide

```bash
curl -sSL https://raw.githubusercontent.com/jordanwinner/hackquest/master/install.sh | bash
```

Ou manuellement :

```bash
git clone https://github.com/jordanwinner/hackquest.git
cd hackquest
bash install.sh
```

## Lancer le jeu

```bash
hackquest
```

## Contrôles

| Touche / mot | Effet |
|---|---|
| `hint` | indice (-5 XP) |
| `skip` | passer la mission |
| `back`, `q` ou **Ctrl+C** | revenir en arrière |
| **Ctrl+D** | quitter |

La progression est enregistrée dans `~/.hackquest_save.json`. Une copie de la version précédente est gardée dans `~/.hackquest_save.json.bak` et sert automatiquement si la sauvegarde est abîmée.

## Ce que tu vas apprendre

- 🐧 **Linux** : navigation, fichiers, permissions, processus, réseau, scripting, avancé
- 🔭 **Nmap** : tous les types de scans
- 🌐 **Web** : recon, SQLi, XSS, JWT, fuzzing
- 🔑 **Mots de passe** : hashcat, john, hydra
- 🕵️ **OSINT** : sherlock, theHarvester, subfinder
- 💥 **Exploitation** : Metasploit, reverse shells, searchsploit
- 🏠 **Post-exploitation** : privesc, persistence
- 🔐 **Crypto** : hashes, RSA, encodages
- 🔬 **Forensics** : PCAP, stéganographie, mémoire
- ⚙️ **Reverse Engineering** : ghidra, gdb, radare2
- 🧨 **PWN** : buffer overflow, ROP
- 🏰 **Active Directory** : kerberoasting, bloodhound
- 📶 **WiFi** : WPA2, handshake
- 🔒 **Jail Escape**

**318 missions — 25 catégories — progression par niveaux**

## Prérequis

- Linux (Kali, Ubuntu, Debian...)
- Python 3.8+
