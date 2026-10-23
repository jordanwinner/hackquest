"""
Sélecteur flou (fzf) pour HackQuest — recherche instantanée parmi toutes les
missions débloquées, avec un aperçu (histoire + objectif) à droite.

Dégradé propre : si fzf n'est pas installé, le jeu garde son menu classique.
Ce fichier sert aussi d'aperçu : `python3 core/fzf.py preview <id_mission>`.
"""
import os
import sys
import subprocess
from shutil import which

# Thème Tokyonight (assorti au reste)
_FZF_COLOR = ("fg:#c0caf5,bg:-1,hl:#7aa2f7,fg+:#ffffff,bg+:#283457,hl+:#bb9af7,"
              "prompt:#7dcfff,pointer:#f7768e,marker:#9ece6a,header:#565f89,"
              "info:#565f89,border:#414868,spinner:#bb9af7")


def fzf_available():
    return which("fzf") is not None


def _cat_title(mid):
    from core.registry import ALL_MISSIONS
    for cdata in ALL_MISSIONS.values():
        if any(m["id"] == mid for m in cdata["missions"]):
            return cdata["title"]
    return ""


def fuzzy_pick_mission(player, prompt_label="Mission"):
    """Ouvre fzf sur les missions débloquées. Renvoie la mission choisie ou None."""
    from core.registry import ALL_MISSIONS, get_mission_by_id
    from core.labs import LABS

    lines = []
    for cat_id, cat_data in ALL_MISSIONS.items():
        if cat_id not in getattr(player, "unlocked_categories", []):
            continue
        for m in cat_data["missions"]:
            done = m["id"] in player.completed_missions
            st = "\033[32m✅\033[0m" if done else "\033[33m○\033[0m"
            lab = "\033[32m💻\033[0m" if m["id"] in LABS else "  "
            cat = f"\033[2m·{cat_data['title']}·\033[0m"
            title = f"\033[2m{m['title']}\033[0m" if done else f"\033[1m{m['title']}\033[0m"
            display = f"{st} {lab} {title}   {cat}   \033[33m+{m['xp']}xp\033[0m"
            # champ caché 1 = id (pour l'aperçu et la récupération)
            lines.append(f"{m['id']}\t{display}")

    if not lines:
        return None

    here = os.path.abspath(__file__)
    preview_cmd = f"python3 {here} preview {{1}}"
    args = [
        "fzf", "--ansi", "--delimiter", "\t", "--with-nth", "2..",
        "--prompt", f"{prompt_label} ❯ ", "--pointer", "▶", "--marker", "✓",
        "--height", "95%", "--layout", "reverse", "--border", "rounded",
        "--info", "inline", "--cycle",
        "--preview", preview_cmd, "--preview-window", "right:52%:wrap:border-left",
        "--header", "⌨  tape pour filtrer   ·   ⏎ jouer   ·   ⎋ revenir",
        "--color", _FZF_COLOR,
    ]
    try:
        # Seul stdout est capturé (la sélection). stderr reste branché sur le
        # terminal : en mode --height, fzf y dessine son interface. Le capturer
        # rendait l'écran vide et le programme gelé (fzf attendait les touches).
        r = subprocess.run(args, input="\n".join(lines), text=True,
                           stdout=subprocess.PIPE)
    except Exception:
        return None
    out = r.stdout.strip()
    if r.returncode != 0 or not out:
        return None
    mid = out.split("\t", 1)[0].strip()
    return get_mission_by_id(mid)


def _preview(mid):
    from core.registry import get_mission_by_id
    from core.labs import LABS
    m = get_mission_by_id(mid)
    if not m:
        print("(mission introuvable)")
        return
    C, B, D, Y, G, M, R = ("\033[36m", "\033[1m", "\033[2m", "\033[33m",
                           "\033[32m", "\033[35m", "\033[0m")
    print(f"{B}{M}🎯 {m['title']}{R}\n")
    print(f"{D}Catégorie{R} : {C}{_cat_title(mid)}{R}")
    if mid in LABS:
        print(f"{D}XP{R}        : {Y}+{m['xp']}{R}     {G}💻 labo interactif (vrai shell){R}")
    else:
        print(f"{D}XP{R}        : {Y}+{m['xp']}{R}")
    print()
    print(f"{B}📖 Histoire{R}")
    print(f"  {m.get('story', '—')}\n")
    print(f"{B}🎯 Objectif{R}")
    print(f"  {m.get('objective', '—')}\n")
    n = len(m.get("hints", []))
    if n:
        print(f"{D}💡 {n} indice(s) disponible(s) — chaque indice coûte un peu d'XP{R}")


if __name__ == "__main__":
    # appelé par fzf pour l'aperçu : on ajoute la racine du projet au chemin
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if len(sys.argv) >= 3 and sys.argv[1] == "preview":
        try:
            _preview(sys.argv[2])
        except Exception as e:
            print("aperçu indisponible :", e)
