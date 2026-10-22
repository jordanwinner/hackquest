"""
Campagne scénarisée : « Opération Nightfall ».

Au lieu de missions isolées, on enchaîne des missions existantes du bac à sable
pour raconter une intrusion complète sur srv-target : reconnaissance → accès →
collecte → élévation → exfiltration. Chaque acte a son texte d'ambiance.

Les missions citées existent déjà (core/labs.py) et se jouent dans le vrai shell
quand Docker est là, sinon en mode texte. La campagne ne débloque rien de force :
elle guide, et compléter une mission compte normalement dans la progression.
"""
from core.ui import (clear, header, separator, press_enter, prompt, slow_print,
                     BOLD, DIM, CYAN, GREEN, YELLOW, RED, MAGENTA, RESET)
from core.registry import get_mission_by_id

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
    press_enter()


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
