import os
import sys
import time

# ── Couleurs ANSI ──────────────────────────────────────────────
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"

def clear():
    # Redessine en place (curseur en haut + efface jusqu'en bas) au lieu de vider
    # tout l'écran : pas de scintillement ni de défilement entre deux choix.
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()

def slow_print(text, delay=0.018):
    """Affiche le texte lettre par lettre pour l'effet narratif."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def banner():
    clear()
    print(f"""{CYAN}{BOLD}
  ██╗  ██╗ █████╗  ██████╗██╗  ██╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗
  ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝
  ███████║███████║██║     █████╔╝ ██║   ██║██║   ██║█████╗  ███████╗   ██║   
  ██╔══██║██╔══██║██║     ██╔═██╗ ██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║   
  ██║  ██║██║  ██║╚██████╗██║  ██╗╚██████╔╝╚██████╔╝███████╗███████║   ██║   
  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚══▀▀╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝   
{RESET}{DIM}  Learn Linux & Cybersecurity by doing — Level up. Hack the world.{RESET}
""")

def header(subtitle=""):
    """En-tête compact pour les écrans de navigation : une ligne au lieu du grand logo,
    pour que passer d'un menu à l'autre ne redessine pas tout l'écran."""
    clear()
    sub = f"  {DIM}·{RESET}  {subtitle}" if subtitle else ""
    print(f"\n  {CYAN}{BOLD}⚡ HACKQUEST{RESET}{sub}")
    separator()

def separator(char="─", width=65, color=DIM):
    print(f"{color}{char * width}{RESET}")

def box(title, content_lines, color=CYAN):
    w = 63
    print(f"{color}┌{'─' * w}┐{RESET}")
    print(f"{color}│{RESET} {BOLD}{title}{RESET}{' ' * (w - len(title) - 1)}{color}│{RESET}")
    print(f"{color}├{'─' * w}┤{RESET}")
    for line in content_lines:
        clean = strip_ansi(line)
        pad = w - len(clean) - 1
        print(f"{color}│{RESET} {line}{' ' * max(0, pad)}{color}│{RESET}")
    print(f"{color}└{'─' * w}┘{RESET}")

def strip_ansi(text):
    import re
    return re.sub(r'\033\[[0-9;]*m', '', text)

def xp_bar(current_xp, next_xp, width=30, level_xp=0):
    """Progression dans le palier actuel (de level_xp à next_xp)."""
    if next_xp is None:
        bar = "█" * width
        return f"{GREEN}{bar}{RESET} MAX"
    ratio = (current_xp - level_xp) / (next_xp - level_xp)
    ratio = min(1, max(0, ratio))
    filled = int(ratio * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{GREEN}{bar}{RESET} {int(ratio * 100)}%"

def success(msg):
    print(f"\n{GREEN}{BOLD}✅ {msg}{RESET}")

def error(msg):
    print(f"\n{RED}{BOLD}❌ {msg}{RESET}")

def info(msg):
    print(f"\n{CYAN}ℹ  {msg}{RESET}")

def warning(msg):
    print(f"\n{YELLOW}⚠  {msg}{RESET}")

def _end_of_input():
    """Ctrl+D ou entrée fermée : plus rien ne pourra être lu, on quitte proprement."""
    print(f"\n{CYAN}  À bientôt ! Ta progression est sauvegardée.{RESET}\n")
    sys.exit(0)

def prompt(text=""):
    """Ctrl+C renvoie "quit" (retour au menu précédent), Ctrl+D quitte le jeu."""
    try:
        sep = " " if text and not text.endswith(" ") else ""
        return input(f"\n{MAGENTA}{BOLD}❯ {text}{sep}{RESET}").strip()
    except KeyboardInterrupt:
        print()
        return "quit"
    except EOFError:
        _end_of_input()

def press_enter():
    try:
        input(f"\n{DIM}[Appuie sur Entrée pour continuer...]{RESET}")
    except KeyboardInterrupt:
        pass
    except EOFError:
        _end_of_input()

def level_up_animation(new_title, new_icon):
    # pas de clear() : le joueur doit encore voir le résultat de sa commande
    # et les catégories débloquées, affichés juste au-dessus
    w = 38
    title = f"Nouveau rang : {new_title}"
    print(f"{YELLOW}{BOLD}")
    print(f"  ╔{'═' * w}╗")
    print(f"  ║     {new_icon}  LEVEL UP !  {new_icon}{' ' * (w - 23)}║")  # emojis : 2 colonnes
    print(f"  ║     {title}{' ' * max(1, w - 5 - len(title))}║")
    print(f"  ╚{'═' * w}╝")
    print(f"{RESET}", end="")
    time.sleep(1.5)

def mission_complete_animation(xp_gained):
    print(f"\n{GREEN}{BOLD}")
    print("  ┌─────────────────────────────┐")
    print("  │   ✅  MISSION ACCOMPLIE !   │")
    print(f"  │   +{xp_gained} XP gagné{' ' * (16 - len(str(xp_gained)))}│")
    print("  └─────────────────────────────┘")
    print(f"{RESET}")
    time.sleep(1.5)
