from core.registry import ALL_MISSIONS as MISSIONS
from core.ui import *  # header, banner, clear, couleurs, prompt...
from core.validate import is_valid_answer, same_tool
from core.labs import LABS, WHERE
from core import sandbox

def show_categories(player):
    """Affiche les catégories disponibles et verrouillées."""
    while True:
        clear()
        header()
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
        if choice == "0" or choice.lower() in ("q", "quit"):
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(available):
                return available[idx]
        except ValueError:
            pass

        error("Choix invalide.")
        press_enter()


def show_missions(player, cat_id, cat_data):
    """Affiche les missions d'une catégorie."""
    while True:
        clear()
        header()
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
            lab = f"  {GREEN}💻 labo{RESET}" if m["id"] in LABS else ""
            print(f"  {num} {BOLD}{m['title']}{RESET}  {DIM}(+{m['xp']} XP){RESET}{lab}")
            print(f"      {status}")
            print(f"      {DIM}{m['objective']}{RESET}\n")

        separator()
        print(f"  {DIM}[0] Retour{RESET}\n")

        choice = prompt("Choix de la mission")
        if choice == "0" or choice.lower() in ("q", "quit", "back"):
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(available):
                return available[idx]
        except ValueError:
            pass

        error("Choix invalide.")
        press_enter()


# État du bac à sable pour la session en cours
_session = {"declined": False, "docker_warned": False}


def _lab_ready(player):
    """True si la mission peut se jouer dans le bac à sable (Docker + image prête)."""
    if not getattr(player, "sandbox", True) or _session["declined"]:
        return False
    if not sandbox.docker_available():
        if not _session["docker_warned"]:
            warning("Docker est indisponible : les missions 💻 se jouent en mode texte.")
            print(f"  {DIM}Installe Docker et ajoute-toi au groupe docker pour le vrai shell.{RESET}")
            _session["docker_warned"] = True
            press_enter()
        return False
    if sandbox.image_ready():
        return True
    clear()
    header()
    print(f"{BOLD}  💻 Le labo n'est pas encore construit{RESET}\n")
    print("  Les missions 💻 se jouent dans un vrai shell, sur un faux serveur isolé")
    print("  (conteneur Docker sans réseau, détruit après chaque mission).")
    print(f"  Il faut le construire une fois : ~300 Mo, quelques minutes, connexion requise.\n")
    if prompt("Construire maintenant ? [O/n]").lower() in ("n", "non", "quit"):
        _session["declined"] = True
        info("Mode texte pour cette session (réglable dans ⚙️ Paramètres).")
        press_enter()
        return False
    print()
    ok = sandbox.build_image(on_line=lambda l: print(f"  {DIM}{l[:100]}{RESET}"))
    if not ok:
        _session["declined"] = True
        error("La construction a échoué (connexion ?). Mode texte pour cette session.")
        press_enter()
        return False
    success("Labo prêt !")
    press_enter()
    return True


def _header(mission, already_done, animate):
    clear()
    header()
    print(f"{BOLD}  📌 {mission['title']}{RESET}  {DIM}(+{mission['xp']} XP){RESET}")
    separator()
    print(f"\n{CYAN}  📖 Histoire :{RESET}")
    for line in mission["story"].split("\n"):
        if animate:
            slow_print(f"     {line}", delay=0.01)
        else:
            print(f"     {line}")
    print(f"\n{YELLOW}  🎯 Objectif :{RESET}")
    print(f"     {mission['objective']}\n")
    if already_done:
        info("Tu as déjà complété cette mission !")


def _hint(player, mission, hint_index):
    """Affiche l'indice suivant (-5 XP). Renvoie le nouvel index."""
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
    return hint_index


def _complete(player, mission, already_done):
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


def run_mission(player, mission):
    """Lance une mission : dans le bac à sable si elle a un labo, sinon en mode texte."""
    spec = LABS.get(mission["id"])
    if spec and _lab_ready(player):
        try:
            return run_lab_mission(player, mission, spec)
        except sandbox.ShellError as e:
            error(f"Le labo n'a pas pu démarrer ({e}). On passe en mode texte.")
            press_enter()
    return run_text_mission(player, mission)


def run_text_mission(player, mission):
    """Mode texte : la commande tapée est comparée à la réponse attendue."""
    already_done = mission["id"] in player.completed_missions
    hint_index = 0
    animate = True

    while True:
        _header(mission, already_done, animate)
        animate = False  # l'histoire ne s'écrit lettre par lettre qu'une fois

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
        if cmd in ("back", "b", "retour", "q", "quit"):
            return

        if cmd in ("skip", "passer"):
            warning("Mission passée.")
            press_enter()
            return

        if cmd == "hint":
            hint_index = _hint(player, mission, hint_index)
            press_enter()
            continue

        # ── Validation de la commande ──
        if is_valid_answer(user_input, mission):
            _complete(player, mission, already_done)
            return

        error(f"Ce n'est pas tout à fait ça... Tape 'hint' si tu bloques.")
        press_enter()


def _shell_input(lab):
    """Lit une commande comme un vrai shell : Ctrl+C annule la ligne,
    Ctrl+D quitte la mission, une commande inachevée continue sur la ligne suivante."""
    ps1 = f"{GREEN}{BOLD}hacker@srv-target{RESET}:{BLUE}{BOLD}{lab.prompt_path()}{RESET}$ "
    try:
        line = input(ps1)
        while line.strip() and sandbox.incomplete(line):
            line += "\n" + input("> ")
        return line
    except KeyboardInterrupt:
        print()  # le terminal a déjà affiché ^C
        return ""
    except EOFError:
        print()
        return "back"


def _lab_help():
    print(f"  {DIM}Commandes du jeu : {YELLOW}hint{RESET}{DIM} (-5 XP) · objectif · reset (labo neuf) · "
          f"clear · skip · back (ou Ctrl+D){RESET}\n")


def run_lab_mission(player, mission, spec):
    """Bac à sable : les commandes s'exécutent pour de vrai dans un conteneur jetable,
    et la mission est validée sur le résultat (flag trouvé, fichier créé, bon dossier...)."""
    already_done = mission["id"] in player.completed_missions
    hint_index = 0

    _header(mission, already_done, animate=True)
    print(f"  {DIM}⚙  Démarrage du labo...{RESET}", end="", flush=True)
    sandbox.cleanup_stale()
    lab = sandbox.Lab(spec)
    try:
        lab.start()
        print(f"\r{GREEN}  💻 Connecté à srv-target{RESET} {DIM}— conteneur isolé, sans réseau, "
              f"détruit à la fin. Casse tout si tu veux.{RESET}")
        if mission["id"] in WHERE:
            print(f"  📂 Fichier de la mission : {CYAN}{WHERE[mission['id']]}{RESET}")
        _lab_help()

        while True:
            line = _shell_input(lab)
            cmd = line.strip()
            if not cmd:
                continue
            word = cmd.lower()

            # ── Commandes du jeu ──
            if word in ("back", "retour", "quit"):
                return
            if word in ("skip", "passer"):
                warning("Mission passée.")
                press_enter()
                return
            if word == "hint":
                hint_index = _hint(player, mission, hint_index)
                print()
                continue
            if word in ("objectif", "obj"):
                print(f"\n{YELLOW}  🎯 {mission['objective']}{RESET}\n")
                continue
            if word in ("aide", "help"):
                _lab_help()
                continue
            if word == "clear":
                clear()
                continue
            if word == "reset":
                print(f"  {DIM}⚙  Labo remis à neuf...{RESET}")
                lab.reset()
                continue

            # ── Vraie commande ──
            code, output, interrupted = lab.run(line)
            if interrupted:
                print(f"{DIM}  ⏱  Commande arrêtée après {lab.timeout} s "
                      f"(dans un vrai terminal, c'est Ctrl+C qui l'arrête).{RESET}")

            right_command = is_valid_answer(line, mission)
            if right_command and lab.check(output, code):
                _complete(player, mission, already_done)
                return
            if right_command:
                print(f"{YELLOW}  ↳ Bonne commande, mais l'objectif n'est pas encore atteint "
                      f"(mauvais fichier ? mauvais dossier ?). Tape 'objectif' ou 'hint'.{RESET}")
            elif same_tool(line, mission):
                print(f"{YELLOW}  ↳ Bonne piste, mais ce n'est pas encore ça : il manque une option "
                      f"ou un argument. Tape 'objectif' ou 'hint'.{RESET}")
    finally:
        lab.close()
