"""
Registre central de toutes les missions.
missions.py (ancien) retiré — remplacé par missions_linux.py + missions_cyber.py
qui sont plus complètes et sans doublons.
"""
from core.missions_linux import get_linux_missions
from core.missions_cyber import get_cyber_missions


def build_full_missions():
    all_missions = {}
    all_missions.update(get_linux_missions())
    all_missions.update(get_cyber_missions())
    return all_missions


ALL_MISSIONS = build_full_missions()


def get_all_missions_flat():
    flat = []
    for cat_id, cat_data in ALL_MISSIONS.items():
        for m in cat_data["missions"]:
            m_copy = dict(m)
            m_copy["category"] = cat_id
            flat.append(m_copy)
    return flat


def get_mission_by_id(mission_id):
    for cat_data in ALL_MISSIONS.values():
        for m in cat_data["missions"]:
            if m["id"] == mission_id:
                return m
    return None


def count_total_missions():
    return sum(len(c["missions"]) for c in ALL_MISSIONS.values())


def count_categories():
    return len(ALL_MISSIONS)


# Ordre de progression recommandé (du plus simple au plus avancé)
PROGRESSION_ORDER = [
    # ── Linux fondamental ──────────────────────────────
    "linux_navigation",
    "linux_files",
    "linux_text",
    "linux_permissions",
    "linux_processes",
    "linux_network",
    "linux_archives",
    "linux_system",
    "linux_scripting",
    "linux_advanced",
    # ── Cybersécurité ──────────────────────────────────
    "nmap_mastery",
    "web_recon",
    "password_attacks",
    "osint_tools",
    "web_attacks",
    "exploitation_tools",
    "post_exploitation",
    "crypto_tools",
    "forensics_tools",
    "reverse_engineering",
    "pwn_tools",
    "network_attacks",
    "active_directory",
    "wifi_hacking",
    "jail_utils",
]

# Catégories débloquées dès le départ
STARTER_CATEGORIES = ["linux_navigation", "linux_files"]

# Déblocages progressifs : compléter X% d'une catégorie débloque la suivante
# Format : { "cat_id": ("cat_à_débloquer", pourcentage_requis) }
UNLOCK_RULES = {
    "linux_navigation":  [("linux_files", 50),    ("linux_text", 100)],
    "linux_files":       [("linux_text", 50),      ("linux_permissions", 100)],
    "linux_text":        [("linux_permissions", 50), ("linux_processes", 100)],
    "linux_permissions": [("linux_processes", 50), ("linux_network", 100)],
    "linux_processes":   [("linux_network", 50),   ("linux_archives", 100)],
    "linux_network":     [("linux_archives", 50),  ("linux_system", 100)],
    "linux_archives":    [("linux_system", 50),    ("linux_scripting", 100)],
    "linux_system":      [("linux_scripting", 50), ("linux_advanced", 100)],
    "linux_scripting":   [("linux_advanced", 50),  ("nmap_mastery", 100)],
    "linux_advanced":    [("nmap_mastery", 50),    ("web_recon", 100)],
    "nmap_mastery":      [("web_recon", 50),       ("osint_tools", 100)],
    "web_recon":         [("password_attacks", 50), ("web_attacks", 100)],
    "password_attacks":  [("web_attacks", 50),     ("osint_tools", 100)],
    "osint_tools":       [("web_attacks", 50),     ("exploitation_tools", 100)],
    "web_attacks":       [("exploitation_tools", 50), ("post_exploitation", 100)],
    "exploitation_tools":[("post_exploitation", 50), ("crypto_tools", 100)],
    "post_exploitation": [("crypto_tools", 50),    ("forensics_tools", 100)],
    "crypto_tools":      [("forensics_tools", 50), ("reverse_engineering", 100)],
    "forensics_tools":   [("reverse_engineering", 50), ("pwn_tools", 100)],
    "reverse_engineering":[("pwn_tools", 50),      ("network_attacks", 100)],
    "pwn_tools":         [("network_attacks", 50), ("active_directory", 100)],
    "network_attacks":   [("active_directory", 50), ("wifi_hacking", 100)],
    "active_directory":  [("wifi_hacking", 50),    ("jail_utils", 100)],
    "wifi_hacking":      [("jail_utils", 50)],
}


def compute_unlocks(player_completed: list, current_unlocked: list) -> list:
    """Calcule les catégories à débloquer selon la progression du joueur."""
    new_unlocks = []
    for cat_id, rules in UNLOCK_RULES.items():
        if cat_id not in current_unlocked:
            continue
        cat_data = ALL_MISSIONS.get(cat_id)
        if not cat_data:
            continue
        total = len(cat_data["missions"])
        if total == 0:
            continue
        done = sum(1 for m in cat_data["missions"] if m["id"] in player_completed)
        pct = (done / total) * 100
        for (unlock_cat, required_pct) in rules:
            if unlock_cat not in current_unlocked and unlock_cat not in new_unlocks and pct >= required_pct:
                new_unlocks.append(unlock_cat)
    return new_unlocks
