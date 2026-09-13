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
    os.system("clear")

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

def xp_bar(current_xp, next_xp, width=30):
    if next_xp is None:
        bar = "█" * width
        return f"{GREEN}{bar}{RESET} MAX"
    filled = int((current_xp / next_xp) * width)
    bar = "█" * filled + "░" * (width - filled)
    pct = int((current_xp / next_xp) * 100)
    return f"{GREEN}{bar}{RESET} {pct}%"

def success(msg):
    print(f"\n{GREEN}{BOLD}✅ {msg}{RESET}")

def error(msg):
    print(f"\n{RED}{BOLD}❌ {msg}{RESET}")

def info(msg):
    print(f"\n{CYAN}ℹ  {msg}{RESET}")

def warning(msg):
    print(f"\n{YELLOW}⚠  {msg}{RESET}")

def prompt(text=""):
    try:
        return input(f"\n{MAGENTA}{BOLD}❯ {text}{RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return "quit"

def press_enter():
    try:
        input(f"\n{DIM}[Appuie sur Entrée pour continuer...]{RESET}")
    except (KeyboardInterrupt, EOFError):
        pass

def level_up_animation(new_title, new_icon):
    clear()
    print(f"\n{YELLOW}{BOLD}")
    print("  ╔══════════════════════════════════════╗")
    print("  ║                                      ║")
    print(f"  ║     {new_icon}  LEVEL UP !  {new_icon}                ║")
    print(f"  ║     Nouveau rang : {new_title:<18}║")
    print("  ║                                      ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{RESET}")
    time.sleep(2)

def mission_complete_animation(xp_gained):
    print(f"\n{GREEN}{BOLD}")
    print("  ┌─────────────────────────────┐")
    print("  │   ✅  MISSION ACCOMPLIE !   │")
    print(f"  │   +{xp_gained} XP gagné{' ' * (20 - len(str(xp_gained)))}│")
    print("  └─────────────────────────────┘")
    print(f"{RESET}")
    time.sleep(1.5)
