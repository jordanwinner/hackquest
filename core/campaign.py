"""
Campagne scénarisée : « Opération Nightfall ».

Au lieu de missions isolées, on enchaîne des missions existantes du bac à sable
pour raconter une intrusion complète sur srv-target : reconnaissance → accès →
collecte → élévation → exfiltration. Chaque acte a son texte d'ambiance.

Les missions citées existent déjà (core/labs.py) et se jouent dans le vrai shell
quand Docker est là, sinon en mode texte. La campagne ne débloque rien de force :
elle guide, et compléter une mission compte normalement dans la progression.
"""
import datetime
import os

from core.ui import (clear, header, separator, press_enter, prompt, slow_print,
                     BOLD, DIM, CYAN, GREEN, YELLOW, RED, MAGENTA, RESET)
from core.registry import get_mission_by_id
from core.labs import LABS

CAMPAIGN = {
    "title": "Opération Nightfall",
    "subtitle": "Compromission de srv-target, du premier scan à l'exfiltration",
    "intro": [
        "Un client te mandate pour un test d'intrusion sur son serveur : srv-target.",
        "Tu n'as qu'une adresse et le feu vert. Objectif : prendre pied, élever tes",
        "privilèges, et prouver l'impact en récupérant des données sensibles.",
        "Chaque acte est une étape réelle. Les flags prouvent ta progression.",
    ],
    "acts": [
        {
            "title": "Acte I — Reconnaissance",
            "brief": "Avant de frapper, on cartographie. Quels ports ? Quel site ? "
                     "Quelles pages cachées ?",
            "missions": ["nmap_01", "net_11", "wrecon_01"],
        },
        {
            "title": "Acte II — Accès initial",
            "brief": "Le portail a un formulaire de connexion mal filtré. On force la "
                     "porte, puis on s'installe en SSH.",
            "missions": ["watk_04", "net_19"],
        },
        {
            "title": "Acte III — Collecte de renseignements",
            "brief": "On est dedans. On fouille les fichiers suspects et le trafic "
                     "capturé pour trouver des secrets.",
            "missions": ["for_03", "for_08"],
        },
        {
            "title": "Acte IV — Élévation de privilèges",
            "brief": "Simple utilisateur pour l'instant. On cherche un binaire SUID, "
                     "des secrets dans l'environnement, et on casse une archive protégée.",
            "missions": ["postex_03", "postex_05", "pass_08"],
        },
        {
            "title": "Acte V — Exfiltration",
            "brief": "Dernier acte : prouver l'impact. On rapatrie le butin et on "
                     "confirme la fuite de données.",
            "missions": ["adv_11", "for_01"],
        },
    ],
    "outro": [
        "srv-target est tombé : accès initial, élévation, et exfiltration démontrée.",
        "C'est exactement le déroulé d'un vrai test d'intrusion.",
        "Rédige ton rapport, hacker. L'opération Nightfall est un succès.",
    ],
}


def _all_mission_ids():
    return [mid for act in CAMPAIGN["acts"] for mid in act["missions"]]


def _progress(player):
    ids = _all_mission_ids()
    done = sum(1 for m in ids if m in player.completed_missions)
    return done, len(ids)


def _intro_screen(player):
    clear()
    header("Campagne")
    print(f"\n  {MAGENTA}{BOLD}🎯 {CAMPAIGN['title']}{RESET}")
    print(f"  {DIM}{CAMPAIGN['subtitle']}{RESET}\n")
    for line in CAMPAIGN["intro"]:
        print(f"  {line}")
    done, total = _progress(player)
    print(f"\n  {CYAN}Progression : {done}/{total} missions{RESET}")
    print(f"\n  {DIM}Dans chaque mission : joue normalement (vrai shell si Docker est là)."
          f" 'skip' passe, 'back' quitte la campagne.{RESET}")
    choice = prompt("[Entrée] commencer · [m] menu").lower()
    return choice not in ("m", "menu", "q", "quit")


import re as _re
_FLAG_RE = _re.compile(r"FLAG\{[^}]+\}")


def _mission_flag(mid):
    spec = LABS.get(mid, {})
    if spec.get("flag"):
        return spec["flag"]
    for alt in spec.get("checks", []):
        out = alt.get("out", [])
        for s in (out if isinstance(out, list) else [out]):
            m = _FLAG_RE.search(s)
            if m:
                return m.group(0)
    return None


REPORT_PATH = os.path.expanduser("~/rapport_nightfall.txt")


def _build_report(player):
    """Construit un rapport de pentest texte à partir des actes de la campagne."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    L = []
    L.append("=" * 68)
    L.append("  RAPPORT DE TEST D'INTRUSION — OPÉRATION NIGHTFALL")
    L.append("=" * 68)
    L.append(f"  Cible    : srv-target")
    L.append(f"  Auditeur : {player.name}")
    L.append(f"  Date     : {now}")
    L.append("")
    L.append("  RÉSUMÉ EXÉCUTIF")
    L.append("  ---------------")
    L.append("  Le serveur srv-target a été compromis de bout en bout : d'un simple")
    L.append("  scan réseau jusqu'à l'exfiltration de données, en passant par un accès")
    L.append("  initial applicatif et une élévation de privilèges. Détail par phase :")
    L.append("")
    severities = ["Reconnaissance", "Élevée", "Élevée", "Critique", "Critique"]
    for i, act in enumerate(CAMPAIGN["acts"]):
        sev = severities[i] if i < len(severities) else "Info"
        L.append(f"  [{i+1}] {act['title']}   (criticité : {sev})")
        for mid in act["missions"]:
            m = get_mission_by_id(mid)
            if not m:
                continue
            state = "OK " if mid in player.completed_missions else "—  "
            L.append(f"      [{state}] {m['title']} : {m['objective']}")
            flag = _mission_flag(mid)
            if flag and mid in player.completed_missions:
                L.append(f"             preuve : {flag}")
        L.append("")
    done = sum(1 for mid in _all_mission_ids() if mid in player.completed_missions)
    L.append("  RECOMMANDATIONS")
    L.append("  ---------------")
    L.append("  - Filtrer les entrées du formulaire de connexion (requêtes préparées).")
    L.append("  - Retirer les binaires SUID inutiles et les secrets des variables d'env.")
    L.append("  - Durcir SSH (clés uniquement), chiffrer les captures et les sauvegardes.")
    L.append("")
    L.append(f"  Progression : {done}/{len(_all_mission_ids())} objectifs atteints.")
    L.append("=" * 68)
    return "\n".join(L)


def _show_report(player):
    report = _build_report(player)
    try:
        with open(REPORT_PATH, "w") as f:
            f.write(report + "\n")
        saved = REPORT_PATH
    except OSError:
        saved = None
    clear()
    header("Rapport")
    print()
    for line in report.splitlines():
        print(f"{DIM if line.startswith('=') else ''}  {line}{RESET}")
    if saved:
        print(f"\n  {GREEN}📄 Rapport enregistré : {saved}{RESET}")
    press_enter()


def _victory(player):
    clear()
    header("Campagne")
    print(f"\n  {GREEN}{BOLD}")
    print("  ╔════════════════════════════════════════════╗")
    print("  ║        🏆  OPÉRATION NIGHTFALL — RÉUSSIE     ║")
    print("  ╚════════════════════════════════════════════╝")
    print(f"{RESET}")
    for line in CAMPAIGN["outro"]:
        print(f"  {line}")
    print()
    if prompt("📄 Générer le rapport de pentest ? [O/n]").lower() not in ("n", "non"):
        _show_report(player)


def play_campaign(player):
    """Déroule la campagne acte par acte. Renvoie quand le joueur sort."""
    from core.game import run_mission  # import tardif : évite toute dépendance circulaire

    done, total = _progress(player)
    if done >= total:
        _victory(player)
        return
    if not _intro_screen(player):
        return

    for act in CAMPAIGN["acts"]:
        # saute un acte déjà entièrement bouclé
        if all(m in player.completed_missions for m in act["missions"]):
            continue
        clear()
        header("Campagne")
        print(f"\n  {MAGENTA}{BOLD}{act['title']}{RESET}\n")
        slow_print(f"  {act['brief']}", delay=0.008)
        press_enter()

        for mid in act["missions"]:
            mission = get_mission_by_id(mid)
            if mission is None:
                continue
            if mid in player.completed_missions:
                print(f"  {GREEN}✅ {mission['title']} — déjà accompli, on enchaîne.{RESET}")
                continue
            res = run_mission(player, mission, chain=False)
            if res == "abort":
                if prompt("Quitter la campagne ? [o/N]").lower() in ("o", "oui", "y"):
                    return
                # sinon on rejoue la même mission
                res2 = run_mission(player, mission, chain=False)
                if res2 == "abort":
                    return
            # 'done' ou 'skip' : on passe à la mission suivante

    _victory(player)
