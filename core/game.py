import atexit

from core.registry import ALL_MISSIONS as MISSIONS, PROGRESSION_ORDER, unlock_hint as unlock_category_hint
from core.ui import *  # header, banner, clear, couleurs, prompt...
from core.validate import is_valid_answer, same_tool
from core.labs import LABS, WHERE
from core import sandbox
from core.simulate import simulated_output

# filet de sécurité : à la fin du jeu, s'assurer qu'aucun conteneur de labo ne traîne
atexit.register(sandbox.cleanup_stale)

def show_categories(player):
    """Affiche les catégories disponibles et verrouillées."""
    while True:
        clear()
        header()
        print(f"{BOLD}  📋 CHOISIR UNE CATÉGORIE{RESET}\n")

        categories = list(MISSIONS.items())
        available = []

        # une ligne par catégorie : la liste des 25 tient à l'écran
        for cat_id, cat_data in categories:
            unlocked = cat_id in player.unlocked_categories
            completed = sum(1 for m in cat_data["missions"] if m["id"] in player.completed_missions)
            total = len(cat_data["missions"])
            title = cat_data["title"]
            if unlocked:
                available.append((cat_id, cat_data))
                num = f"{CYAN}{BOLD}[{len(available)}]{RESET}"
                done = f"{GREEN}✅ {completed}/{total}{RESET}" if completed == total and total \
                    else f"{GREEN}{completed}{RESET}{DIM}/{total}{RESET}"
                print(f"  {num:>4} {title}  {done}")
            else:
                hint = unlock_category_hint(cat_id)
                tip = f"{DIM} — 🔒 {hint}{RESET}" if hint else ""
                print(f"  {DIM}[🔒] {title}{RESET}{tip}")

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

        # une ligne par mission : coche, titre, XP, badge labo
        for i, m in enumerate(missions):
            done = m["id"] in player.completed_missions
            mark = f"{GREEN}✅{RESET}" if done else f"{YELLOW}·{RESET}"
            available.append(m)
            num = f"{CYAN}{BOLD}[{i+1}]{RESET}"
            lab = f" {GREEN}💻{RESET}" if m["id"] in LABS else "   "
            title = f"{DIM}{m['title']}{RESET}" if done else f"{BOLD}{m['title']}{RESET}"
            print(f"  {mark} {num:>4}{lab} {title}  {DIM}(+{m['xp']} XP){RESET}")

        print(f"\n  {DIM}Astuce : tape le numéro d'une mission. Objectif détaillé une fois dedans.{RESET}\n")
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
    print(f"  Il faut le construire une fois : ~830 Mo, quelques minutes, connexion requise.")
    print(f"  {DIM}(Sur Mac Apple Silicon, cette 1re construction est plus longue — c'est normal.){RESET}\n")
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


def _category_of(mid):
    for cid, cat in MISSIONS.items():
        if any(m["id"] == mid for m in cat["missions"]):
            return cid
    return None


def _next_mission(player, mission):
    """Mission qui suit : la suivante dans la catégorie, sinon la 1re de la
    prochaine catégorie débloquée. Renvoie (cat_id, mission) ou (None, None)."""
    cid = _category_of(mission["id"])
    if cid is None:
        return None, None
    missions = MISSIONS[cid]["missions"]
    idx = next(i for i, m in enumerate(missions) if m["id"] == mission["id"])
    if idx + 1 < len(missions):
        return cid, missions[idx + 1]
    order = PROGRESSION_ORDER
    for nid in order[order.index(cid) + 1:] if cid in order else []:
        if nid in player.unlocked_categories and MISSIONS[nid]["missions"]:
            return nid, MISSIONS[nid]["missions"][0]
    return None, None


def _after_mission(player, mission):
    """Affiché après une réussite. Renvoie la mission suivante à jouer,
    ou \"list\" (liste des missions) ou \"menu\" (menu principal)."""
    cid, nxt = _next_mission(player, mission)
    print()
    separator()
    if nxt:
        if cid == _category_of(mission["id"]):
            print(f"  {GREEN}{BOLD}[Entrée]{RESET} ➡  Mission suivante : {BOLD}{nxt['title']}{RESET} "
                  f"{DIM}(+{nxt['xp']} XP){RESET}")
        else:
            print(f"  {GREEN}{BOLD}[Entrée]{RESET} 🆙 Niveau suivant — {MISSIONS[cid]['title']} : "
                  f"{BOLD}{nxt['title']}{RESET}")
    print(f"  {CYAN}[l]{RESET} 📋 Liste des missions")
    print(f"  {DIM}[m]{RESET} 🏠 Menu principal")
    choice = prompt("Et maintenant ?").lower()
    if choice in ("m", "menu", "quit"):
        return "menu"
    if choice in ("l", "list", "liste", "back", "b"):
        return "list"
    return nxt if nxt else "list"


def run_mission(player, mission, chain=True):
    """Lance une mission : dans le bac à sable si elle a un labo, sinon en mode texte.
    chain=False (mode campagne) : à la réussite, renvoie 'done' au lieu du menu
    'Et maintenant ?' ; back renvoie 'abort', skip renvoie 'skip'."""
    spec = LABS.get(mission["id"])
    if spec and _lab_ready(player):
        try:
            return run_lab_mission(player, mission, spec, chain=chain)
        except sandbox.ShellError as e:
            error(f"Le labo n'a pas pu démarrer ({e}). On passe en mode texte.")
            press_enter()
    return run_text_mission(player, mission, chain=chain)


def run_text_mission(player, mission, chain=True):
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
            return "abort" if not chain else "list"

        if cmd in ("skip", "passer"):
            warning("Mission passée.")
            press_enter()
            return "skip" if not chain else "list"

        if cmd == "hint":
            hint_index = _hint(player, mission, hint_index)
            press_enter()
            continue

        # ── Validation de la commande ──
        if is_valid_answer(user_input, mission):
            sample = simulated_output(user_input)
            if sample:
                print(f"\n{sample}")
            _complete(player, mission, already_done)
            return "done" if not chain else _after_mission(player, mission)

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


# Programmes plein écran ou qui attendent le clavier : le labo n'a pas de vrai
# terminal, on explique plutôt que de laisser une erreur obscure.
_INTERACTIVE = {
    "top": "pas d'affichage plein écran ici : essaie `top -b -n 1` ou `ps aux`.",
    "htop": "pas d'affichage plein écran ici : essaie `top -b -n 1` ou `ps aux`.",
    "vim": "pas d'éditeur ici : écris avec `echo 'texte' > fichier` ou `cat > fichier << EOF`.",
    "vi": "pas d'éditeur ici : écris avec `echo 'texte' > fichier` ou `cat > fichier << EOF`.",
    "nano": "pas d'éditeur ici : écris avec `echo 'texte' > fichier` ou `cat > fichier << EOF`.",
    "python3": "pas de console interactive ici : lance `python3 -c '...'` ou `python3 script.py`.",
    "python": "pas de console interactive ici : lance `python3 -c '...'` ou `python3 script.py`.",
    "bash": "tu es déjà dans bash : pas besoin d'en ouvrir un autre.",
    "sh": "tu es déjà dans un shell : pas besoin d'en ouvrir un autre.",
}


def _interactive_tip(cmd):
    """Conseil si la commande lance un programme interactif, sinon None."""
    parts = cmd.split()
    if not parts or parts[0] not in _INTERACTIVE:
        return None
    if parts[0] == "top" and "-b" in parts:
        return None
    if parts[0] in ("python3", "python", "bash", "sh") and len(parts) > 1:
        return None
    return _INTERACTIVE[parts[0]]


import re as _re
_FLAG_RE = _re.compile(r"FLAG\{[^}]+\}")


def _mission_flag(spec):
    """Déduit le flag attendu d'une mission : champ `flag` explicite, sinon un
    FLAG{...} présent dans les `checks` (valeurs `out`). None sinon (ls, cd...)."""
    if spec.get("flag"):
        return spec["flag"]
    for alt in spec.get("checks", []):
        out = alt.get("out", [])
        for s in (out if isinstance(out, list) else [out]):
            m = _FLAG_RE.fullmatch(s) or _FLAG_RE.search(s)
            if m:
                return m.group(0)
    return None


def _flag_submission(cmd, flag):
    """Interprète une tentative de soumission de flag. Renvoie 'ok', 'ko' ou None
    (= ce n'est pas une soumission, à traiter comme une commande shell)."""
    parts = cmd.split(maxsplit=1)
    head = parts[0].lower()
    if head in ("flag", "submit", "soumets", "soumettre") and len(parts) == 2:
        candidate = parts[1].strip().strip("'\"")
    elif cmd.strip().startswith("FLAG{"):
        candidate = cmd.strip()
    else:
        return None
    return "ok" if candidate == flag else "ko"


def _lab_help(has_flag=False):
    extra = (f"\n  {DIM}🚩 Quand tu trouves le flag, {YELLOW}soumets-le{RESET}{DIM} : tape-le "
             f"directement (ou « submit FLAG{{...}} »).{RESET}") if has_flag else ""
    print(f"  {DIM}Commandes du jeu : {YELLOW}hint{RESET}{DIM} (-5 XP) · objectif · reset (labo neuf) · "
          f"clear · skip · back (ou Ctrl+D){RESET}{extra}\n")


def run_lab_mission(player, mission, spec, chain=True):
    """Bac à sable : les commandes s'exécutent pour de vrai dans un conteneur jetable,
    et la mission est validée sur le résultat (flag trouvé, fichier créé, bon dossier...)."""
    already_done = mission["id"] in player.completed_missions
    hint_index = 0
    flag = _mission_flag(spec)
    # Les vraies missions CTF (hors Linux de base) exigent de soumettre le flag :
    # lancer la bonne commande ne suffit pas, il faut avoir lu le résultat.
    category = _category_of(mission["id"]) or ""
    require_flag = bool(flag) and not category.startswith("linux_")

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
        _lab_help(has_flag=bool(flag))

        while True:
            line = _shell_input(lab)
            cmd = line.strip()
            if not cmd:
                continue
            word = cmd.lower()

            # ── Commandes du jeu ──
            if word in ("back", "retour", "quit"):
                return "abort" if not chain else "list"
            if word in ("skip", "passer"):
                warning("Mission passée.")
                press_enter()
                return "skip" if not chain else "list"
            if word == "hint":
                hint_index = _hint(player, mission, hint_index)
                print()
                continue
            if word in ("objectif", "obj"):
                print(f"\n  {DIM}📖 {mission['story']}{RESET}")
                print(f"{YELLOW}  🎯 {mission['objective']}{RESET}")
                if mission["id"] in WHERE:
                    print(f"  📂 Fichier de la mission : {CYAN}{WHERE[mission['id']]}{RESET}")
                print()
                continue
            if word in ("aide", "help"):
                _lab_help(has_flag=bool(flag))
                continue
            if word == "clear":
                clear()
                continue

            # ── Soumission du flag (vraie sensation CTF : il faut l'avoir lu) ──
            if flag:
                verdict = _flag_submission(cmd, flag)
                if verdict == "ok":
                    print(f"{GREEN}  🚩 Flag correct !{RESET}")
                    _complete(player, mission, already_done)
                    return "done" if not chain else _after_mission(player, mission)
                if verdict == "ko":
                    print(f"{RED}  🚩 Mauvais flag. Relis la sortie de ta commande.{RESET}")
                    continue
            if word == "reset":
                print(f"  {DIM}⚙  Labo remis à neuf...{RESET}")
                lab.reset()
                continue

            # ── Vraie commande ──
            tip = _interactive_tip(cmd)
            if tip:
                print(f"{YELLOW}  ↳ {tip}{RESET}")
                continue
            code, output, interrupted = lab.run(line)
            if interrupted == "ctrl-c":
                print(f"{DIM}  ⏹  Commande arrêtée (Ctrl+C).{RESET}")
            elif interrupted:
                print(f"{DIM}  ⏱  Commande arrêtée après {lab.timeout} s "
                      f"(dans un vrai terminal, c'est Ctrl+C qui l'arrête).{RESET}")

            right_command = is_valid_answer(line, mission)
            if right_command and lab.check(output, code):
                if require_flag:
                    print(f"{GREEN}  ✅ Commande réussie — le flag est dans la sortie. "
                          f"{BOLD}Soumets-le pour valider{RESET}{GREEN} (tape-le directement).{RESET}")
                else:
                    _complete(player, mission, already_done)
                    return "done" if not chain else _after_mission(player, mission)
            elif right_command:
                print(f"{YELLOW}  ↳ Bonne commande, mais l'objectif n'est pas encore atteint "
                      f"(mauvais fichier ? mauvais dossier ?). Tape 'objectif' ou 'hint'.{RESET}")
            elif same_tool(line, mission):
                print(f"{YELLOW}  ↳ Bonne piste, mais ce n'est pas encore ça : il manque une option "
                      f"ou un argument. Tape 'objectif' ou 'hint'.{RESET}")
    finally:
        lab.close()
