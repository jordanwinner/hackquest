import json
import os
from datetime import datetime

SAVE_FILE = os.path.expanduser("~/.hackquest_save.json")

LEVELS = [
    (0,    "Newbie",         "⚪"),
    (100,  "Script Kiddie",  "🟢"),
    (300,  "Hacker",         "🔵"),
    (600,  "Elite Hacker",   "🟣"),
    (1000, "Cyber Ninja",    "🔴"),
    (1500, "Shadow Agent",   "🟠"),
    (2500, "Ghost Operator", "⭐"),
    (4000, "Legend",         "💀"),
]

# Anciennes catégories supprimées (missions.py retiré)
_LEGACY_CATEGORIES = {
    "linux_basics", "recon", "web", "exploitation",
    "post_exploit", "crypto", "forensics",
}

# Correspondance anciens IDs → nouveaux IDs équivalents
# (missions de missions.py vers missions_linux/cyber)
_LEGACY_MISSION_MAP = {
    # linux_basics → linux_navigation + linux_files + linux_text + linux_processes
    "lb_01": "nav_01",  # pwd
    "lb_02": "nav_02",  # ls
    "lb_03": "nav_05",  # cd
    "lb_04": "fil_01",  # cat
    "lb_05": "txt_01",  # grep
    "lb_06": "nav_09",  # find
    "lb_07": "nav_01",  # whoami → on mappe sur nav_01 (pas d'équivalent exact)
    "lb_08": "fil_16",  # stat / ls -l
    "lb_09": "txt_01",  # pipe → txt_01
    "lb_10": "proc_01",  # ps aux  (linux_processes)
    # recon → nmap_mastery + osint_tools + web_recon
    "rc_01": "nmap_01",
    "rc_02": "nmap_04",
    "rc_03": "osint_01",
    "rc_04": "osint_04",
    "rc_05": "osint_02",
    # web → web_attacks + web_recon
    "web_01": "wr_01",
    "web_02": "wa_01",
    "web_03": "wa_05",
    "web_04": "wa_08",
    "web_05": "wr_05",
    # exploitation → exploitation_tools
    "ex_01": "et_01",
    "ex_02": "et_02",
    "ex_03": "et_03",
    "ex_04": "et_04",
    # post_exploit → post_exploitation
    "pe_01": "post_01",
    "pe_02": "post_02",
    "pe_03": "post_03",
    # crypto → crypto_tools
    "cr_01": "ct_01",
    "cr_02": "ct_02",
    "cr_03": "ct_03",
    "cr_04": "ct_04",
    # forensics → forensics_tools
    "fo_01": "ft_01",
    "fo_02": "ft_06",
    "fo_03": "ft_08",
}


def _migrate_save(data: dict) -> dict:
    """Migre une sauvegarde ancienne vers le nouveau format."""
    completed = data.get("completed_missions", [])
    unlocked  = data.get("unlocked_categories", [])

    # Remplacer les anciens IDs par les nouveaux
    new_completed = []
    for mid in completed:
        mapped = _LEGACY_MISSION_MAP.get(mid, mid)
        if mapped not in new_completed:
            new_completed.append(mapped)

    # Retirer les anciennes catégories supprimées
    new_unlocked = [c for c in unlocked if c not in _LEGACY_CATEGORIES]
    # Toujours avoir les catégories de départ
    for starter in ("linux_navigation", "linux_files"):
        if starter not in new_unlocked:
            new_unlocked.insert(0, starter)

    data["completed_missions"]  = new_completed
    data["unlocked_categories"] = new_unlocked
    data["_migrated"]           = True
    return data


class Player:
    def __init__(self):
        self.name = "Hacker"
        self.xp = 0
        self.level = 0
        self.completed_missions = []
        self.unlocked_categories = ["linux_navigation", "linux_files"]
        self.hints_used = 0
        self.created_at = datetime.now().isoformat()

    def get_level_info(self):
        current = LEVELS[0]
        next_level = None
        for i, (xp_req, title, icon) in enumerate(LEVELS):
            if self.xp >= xp_req:
                current = (xp_req, title, icon)
                self.level = i
            else:
                next_level = (xp_req, title, icon)
                break
        return current, next_level

    def add_xp(self, amount, reason=""):
        old_level = self.level
        self.xp += amount
        self.get_level_info()
        leveled_up = self.level > old_level
        return leveled_up

    def complete_mission(self, mission_id):
        if mission_id not in self.completed_missions:
            self.completed_missions.append(mission_id)

    def unlock_category(self, category):
        if category not in self.unlocked_categories:
            self.unlocked_categories.append(category)

    def check_and_apply_unlocks(self):
        """Vérifie et applique les déblocages de catégories selon la progression."""
        from core.registry import compute_unlocks
        new_unlocks = compute_unlocks(self.completed_missions, self.unlocked_categories)
        for cat in new_unlocks:
            self.unlock_category(cat)
        return new_unlocks

    def save(self):
        data = {
            "name": self.name,
            "xp": self.xp,
            "level": self.level,
            "completed_missions": self.completed_missions,
            "unlocked_categories": self.unlocked_categories,
            "hints_used": self.hints_used,
            "created_at": self.created_at,
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if not os.path.exists(SAVE_FILE):
            return False
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)

            # Migration automatique des anciennes sauvegardes
            if not data.get("_migrated"):
                data = _migrate_save(data)
                # Sauvegarder la version migrée immédiatement
                with open(SAVE_FILE, "w") as f:
                    json.dump(data, f, indent=2)

            self.name = data.get("name", "Hacker")
            self.xp = data.get("xp", 0)
            self.level = data.get("level", 0)
            self.completed_missions = data.get("completed_missions", [])
            self.unlocked_categories = data.get("unlocked_categories", ["linux_navigation", "linux_files"])
            self.hints_used = data.get("hints_used", 0)
            self.created_at = data.get("created_at", datetime.now().isoformat())
            # Applique les déblocages au chargement
            self.check_and_apply_unlocks()
            return True
        except Exception:
            return False

    def stats(self):
        current, next_lvl = self.get_level_info()
        xp_req, title, icon = current
        lines = [
            f"\n  {icon} {self.name}  —  {title}",
            f"  XP       : {self.xp}",
        ]
        if next_lvl:
            nxp, ntitle, nicon = next_lvl
            lines.append(f"  Prochain : {ntitle} ({nxp - self.xp} XP restants)")
        lines.append(f"  Missions : {len(self.completed_missions)} complétées")
        lines.append(f"  Indices  : {self.hints_used} utilisés")
        return "\n".join(lines)
