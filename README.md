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

## 💻 Bac à sable

Les missions marquées **💻 labo** se jouent dans un **vrai shell**, sur `srv-target`, un faux serveur compromis rempli de logs, de fichiers cachés et de flags. Une mission n'est validée que si **le résultat est là** : flag affiché, fichier créé, bon dossier atteint…

Les missions **Linux locales**, la **forensics**, le **reverse engineering local** et la **post-exploitation locale** ont un labo — 113 missions dans le vrai shell. La forensics travaille sur de vrais fichiers plantés dans le serveur : image aux métadonnées cachées (exiftool), fichier embarqué (binwalk), stéganographie (steghide), carving (foremost), capture réseau (tshark), règle YARA, entropie, et un crackme à analyser (strings, strace, ltrace, gdb, checksec)… Les catégories qui ont besoin d'une cible réseau ou distante (Nmap, Web, OSINT, Active Directory…) restent en mode texte, puisque le labo n'a **pas de réseau** par choix de sécurité.

- Il faut **Docker**. Sans Docker, ces missions se jouent en mode texte. Pour l'installer (Ubuntu/Debian/Kali) :

  ```bash
  sudo apt install docker.io
  sudo usermod -aG docker $USER
  ```

  Ensuite, **déconnecte-toi puis reconnecte-toi** pour que le groupe `docker` soit pris en compte. Pour vérifier : `docker run --rm hello-world`.
- Le labo est construit automatiquement au premier lancement : ~600 Mo, une seule fois, connexion requise.
- Chaque mission tourne dans un conteneur **sans réseau**, en utilisateur non-root, **détruit à la fin**. Tu peux tout casser sans risque.
- Pour changer de mode : ⚙️ Paramètres → Bac à sable.

Dans le labo : `hint`, `objectif`, `reset` (labo remis à neuf), `clear`, `skip`, `back`. **Ctrl+C** arrête une commande, **Ctrl+D** quitte la mission.

Pour vérifier que chaque labo est faisable :

```bash
python3 tests/test_labs.py
```

Ce script joue la solution de chaque labo, qui doit réussir, puis une mauvaise commande, qui doit échouer. Le monde du labo est décrit dans `lab/world.py`, et les objectifs dans `core/labs.py`.

## Contrôles

| Touche / mot | Effet |
|---|---|
| `hint` | indice (-5 XP) |
| `skip` | passer la mission |
| `back`, `q` ou **Ctrl+C** | revenir en arrière (dans un labo, Ctrl+C arrête la commande) |
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
- Optionnel : Docker, pour les missions 💻 (voir plus haut). Un labo utilise ~1 Mo de RAM au repos (256 Mo au maximum) et l'image occupe ~600 Mo (outils de forensics inclus).

## Mettre à jour

Relance la commande d'installation : elle fait un `git pull` et ta progression est conservée. Si le labo a changé, le jeu propose de le reconstruire.
