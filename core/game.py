from core.registry import ALL_MISSIONS as MISSIONS
from core.ui import *

def show_categories(player):
    """Affiche les catégories disponibles et verrouillées."""
    clear()
    banner()
    print(f"{BOLD}  📋 CHOISIR UNE CATÉGORIE{RESET}\n")

    categories = list(MISSIONS.items())
    available = []

    for i, (cat_id, cat_data) in enumerate(categories):
        unlocked = cat_id in player.unlocked_categories
        completed = sum(
            1 for m in cat_data["missions"]
            if m["id"] in player.completed_missions
        )
        total = len(cat_data["missions"])

        if unlocked:
            status = f"{GREEN}✅ {completed}/{total}{RESET}"
            idx = len(available)
            available.append((cat_id, cat_data))
            print(f"  {CYAN}{BOLD}[{idx + 1}]{RESET} {cat_data['title']}")
            print(f"      {DIM}{cat_data['description']}{RESET}")
            print(f"      Progression : {status}")
        else:
            print(f"  {DIM}[🔒] {cat_data['title']} — {cat_data['description']}{RESET}")
        print()

    separator()
    print(f"  {DIM}[0] Retour au menu principal{RESET}\n")

    choice = prompt("Choix")
    if choice == "0" or choice.lower() == "q":
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(available):
            return available[idx]
    except ValueError:
        pass

    error("Choix invalide.")
    press_enter()
    return show_categories(player)


def show_missions(player, cat_id, cat_data):
    """Affiche les missions d'une catégorie."""
    clear()
    banner()
    print(f"{BOLD}  {cat_data['title']}{RESET}\n")

    missions = cat_data["missions"]
    available = []

    for i, m in enumerate(missions):
        done = m["id"] in player.completed_missions
        if done:
            status = f"{GREEN}✅ Complétée{RESET}"
        else:
            status = f"{YELLOW}⏳ En attente{RESET}"
        available.append(m)
        num = f"{CYAN}{BOLD}[{i+1}]{RESET}"
        print(f"  {num} {BOLD}{m['title']}{RESET}  {DIM}(+{m['xp']} XP){RESET}")
        print(f"      {status}")
        print(f"      {DIM}{m['objective']}{RESET}\n")

    separator()
    print(f"  {DIM}[0] Retour{RESET}\n")

    choice = prompt("Choix de la mission")
    if choice == "0" or choice.lower() in ("q", "back"):
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(available):
            return available[idx]
    except ValueError:
        pass

    error("Choix invalide.")
    press_enter()
    return show_missions(player, cat_id, cat_data)


def run_mission(player, mission):
    """Lance une mission interactive."""
    already_done = mission["id"] in player.completed_missions
    hint_index = 0

    while True:
        clear()
        banner()

        # En-tête mission
        print(f"{BOLD}  📌 {mission['title']}{RESET}  {DIM}(+{mission['xp']} XP){RESET}")
        separator()

        # Histoire
        print(f"\n{CYAN}  📖 Histoire :{RESET}")
        for line in mission["story"].split("\n"):
            slow_print(f"     {line}", delay=0.01)

        # Objectif
        print(f"\n{YELLOW}  🎯 Objectif :{RESET}")
        print(f"     {mission['objective']}\n")

        if already_done:
            info("Tu as déjà complété cette mission !")

        separator()
        print(f"\n  Commandes disponibles :")
        print(f"  {CYAN}[commande]{RESET}  Tape la commande attendue pour valider")
        print(f"  {YELLOW}hint{RESET}        Affiche un indice (-5 XP)")
        print(f"  {DIM}skip{RESET}        Passe cette mission")
        print(f"  {DIM}back{RESET}        Retour à la liste\n")

        user_input = prompt()

        if not user_input:
            continue

        cmd = user_input.lower().strip()

        # ── Commandes spéciales ──
        if cmd in ("back", "b", "retour"):
            return

        if cmd in ("skip", "passer"):
            warning("Mission passée.")
            press_enter()
            return

        if cmd == "hint":
            hints = mission.get("hints", [])
            if not hints:
                info("Pas d'indices pour cette mission.")
            elif hint_index < len(hints):
                print(f"\n{YELLOW}  💡 Indice {hint_index + 1}/{len(hints)} :{RESET}")
                print(f"     {hints[hint_index]}")
                hint_index += 1
                player.hints_used += 1
                player.xp = max(0, player.xp - 5)
                player.save()
                info("-5 XP pour l'utilisation d'un indice.")
            else:
                info("Tu as utilisé tous les indices disponibles.")
            press_enter()
            continue

        # ── Validation de la commande ──
        accept = mission.get("accept_contains", [])
        validated = any(keyword.lower() in user_input.lower() for keyword in accept)

        if validated:
            mission_complete_animation(mission["xp"])

            if not already_done:
                leveled_up = player.add_xp(mission["xp"], mission["title"])
                player.complete_mission(mission["id"])

                # Déblocages dynamiques selon progression
                new_unlocks = player.check_and_apply_unlocks()
                for unlock in new_unlocks:
                    from core.registry import ALL_MISSIONS
                    cat_title = ALL_MISSIONS.get(unlock, {}).get("title", unlock.replace("_", " ").title())
                    print(f"\n{MAGENTA}{BOLD}  🔓 Nouvelle catégorie débloquée : {cat_title} !{RESET}")

                # Déblocages explicites dans la mission (compatibilité)
                for unlock in mission.get("unlocks", []):
                    if unlock not in player.unlocked_categories:
                        player.unlock_category(unlock)

                if leveled_up:
                    from core.player import LEVELS
                    _, lvl_title, lvl_icon = LEVELS[player.level]
                    level_up_animation(lvl_title, lvl_icon)

                player.save()
            else:
                info("Mission déjà complétée — pas d'XP supplémentaire.")

            press_enter()
            return

        else:
            error(f"Ce n'est pas tout à fait ça... Tape 'hint' si tu bloques.")
            press_enter()
