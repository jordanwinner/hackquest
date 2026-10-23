#!/usr/bin/env bash
# HackQuest — script d'installation
# Usage : ./install.sh

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

INSTALL_DIR="$HOME/.hackquest"
REPO_URL="https://github.com/jordanwinner/hackquest.git"
BIN_DIR="$HOME/.local/bin"

# ── Installation de dépendances (systèmes apt : Ubuntu/Debian) ─────────────
# sudo seulement si on n'est pas déjà root et que sudo existe.
SUDO=""
[ "$(id -u)" -ne 0 ] && command -v sudo &>/dev/null && SUDO="sudo"
HAS_APT=0; command -v apt-get &>/dev/null && HAS_APT=1
_apt_updated=0

apt_install() {                 # $1 = paquet ; renvoie 0 si installé avec succès
    [ "$HAS_APT" = 1 ] || return 1
    if [ "$_apt_updated" = 0 ]; then $SUDO apt-get update -qq && _apt_updated=1; fi
    $SUDO apt-get install -y -qq "$1" >/dev/null 2>&1
}

echo -e "\n${CYAN}${BOLD}"
echo "  ██╗  ██╗ █████╗  ██████╗██╗  ██╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗"
echo "  ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝"
echo "  ███████║███████║██║     █████╔╝ ██║   ██║██║   ██║█████╗  ███████╗   ██║   "
echo "  ██╔══██║██╔══██║██║     ██╔═██╗ ██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║   "
echo "  ██║  ██║██║  ██║╚██████╗██║  ██╗╚██████╔╝╚██████╔╝███████╗███████║   ██║   "
echo "  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚══▀▀╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝   "
echo -e "${NC}"
echo -e "  ${BOLD}Installation de HackQuest${NC}\n"

# ── Vérifier (et installer si besoin) Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "  ⚙  Python 3 manquant : installation..."
    apt_install python3 || true
    if ! command -v python3 &>/dev/null; then
        echo -e "${RED}❌ Python 3 est requis. Installe-le avec : sudo apt install python3${NC}"
        exit 1
    fi
fi

PYTHON_VERSION=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$PYTHON_VERSION" -lt 8 ]; then
    echo -e "${RED}❌ Python 3.8+ requis (tu as Python 3.$PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "  ${GREEN}✅ Python 3 détecté${NC}"

# ── Récupérer le jeu
# Lancé depuis un clone : on utilise ce dossier tel quel (pas de copie qui divergerait).
# Lancé via `curl | bash` : il n'y a pas de dossier, on clone le repo dans ~/.hackquest.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)"
if [ -f "$SCRIPT_DIR/hackquest.py" ]; then
    GAME_DIR="$SCRIPT_DIR"
    echo -e "  ${GREEN}✅ Jeu trouvé dans $GAME_DIR${NC}"
else
    if ! command -v git &>/dev/null; then
        echo -e "  ⚙  git manquant : installation..."
        apt_install git || true
        command -v git &>/dev/null || { echo -e "${RED}❌ git est requis : sudo apt install git${NC}"; exit 1; }
    fi
    GAME_DIR="$INSTALL_DIR"
    if [ -d "$GAME_DIR/.git" ]; then
        echo -e "  🔄 Mise à jour de $GAME_DIR..."
        git -C "$GAME_DIR" pull --ff-only -q
    else
        echo -e "  📥 Téléchargement dans $GAME_DIR..."
        git clone -q "$REPO_URL" "$GAME_DIR"
    fi
    echo -e "  ${GREEN}✅ Fichiers prêts${NC}"
fi

# ── fzf (optionnel) : recherche floue des missions avec aperçu
if command -v fzf &>/dev/null; then
    echo -e "  ${GREEN}✅ fzf présent (recherche floue des missions activée)${NC}"
elif [ "$HAS_APT" = 1 ]; then
    echo -e "  ⚙  fzf manquant : installation (recherche floue des missions)..."
    if apt_install fzf; then
        echo -e "  ${GREEN}✅ fzf installé${NC}"
    else
        echo -e "  ${DIM:-}ℹ  fzf non installé — le menu classique sera utilisé.${NC}"
    fi
else
    echo -e "  ℹ  fzf absent — menu classique (installe fzf pour la recherche floue)."
fi

# ── Créer la commande hackquest dans ~/.local/bin
mkdir -p "$BIN_DIR"
chmod +x "$GAME_DIR/hackquest"
ln -sf "$GAME_DIR/hackquest" "$BIN_DIR/hackquest"

echo -e "  ${GREEN}✅ Commande 'hackquest' installée dans $BIN_DIR${NC}"

# ── Enregistrer ~/.local/bin dans le PATH, pour que `hackquest` soit lançable
#    depuis n'importe où, à chaque session, sans rien retaper.
PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'

add_to_path() {              # ajoute la ligne à un fichier shell existant (0 = fichier présent)
    local rc="$1"
    [ -f "$rc" ] || return 1
    if ! grep -qF -e "$BIN_DIR" -e '$HOME/.local/bin' "$rc" 2>/dev/null; then
        printf '\n# ajouté par HackQuest\n%s\n' "$PATH_LINE" >> "$rc"
        echo -e "  ${GREEN}✅ PATH enregistré dans $rc${NC}"
    fi
    return 0
}

SHELL_RC=""
case ":$PATH:" in
    *":$BIN_DIR:"*)
        echo -e "  ${GREEN}✅ $BIN_DIR est déjà dans le PATH${NC}" ;;
    *)
        found=0
        for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
            add_to_path "$rc" && found=1
        done
        if [ "$found" = 0 ]; then       # aucun fichier shell : on crée ~/.profile
            printf '%s\n' "$PATH_LINE" > "$HOME/.profile"
            echo -e "  ${GREEN}✅ PATH enregistré dans $HOME/.profile${NC}"
        fi
        # fichier à « sourcer » pour en profiter tout de suite
        [ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"
        [ -n "$ZSH_VERSION" ] && [ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"
        ;;
esac

# ── Test rapide
echo -e "\n  🧪 Test de démarrage..."
if python3 -c "
import sys
sys.path.insert(0, '$GAME_DIR')
from core.registry import count_total_missions
print(f'  {count_total_missions()} missions chargées')
" 2>/dev/null; then
    echo -e "\n${GREEN}${BOLD}  ✅ HackQuest installé avec succès !${NC}"
else
    echo -e "\n${RED}  ❌ Erreur lors du test. Vérifie les fichiers.${NC}"
    exit 1
fi

# ── Docker (optionnel) : nécessaire pour les missions 💻 dans le vrai shell
#    On ne l'installe pas en douce : il modifie le système (démon + groupe + reconnexion).
#    → proposé seulement en interactif, ou forcé avec HQ_INSTALL_DOCKER=1.
install_docker() {
    echo -e "  ⚙  Installation de Docker..."
    apt_install docker.io || return 1
    [ -n "$SUDO" ] && $SUDO usermod -aG docker "$USER" 2>/dev/null
    command -v docker &>/dev/null
}

if command -v docker &>/dev/null; then
    if docker info &>/dev/null; then
        echo -e "  ${GREEN}✅ Docker opérationnel : les missions 💻 se joueront dans un vrai shell${NC}"
    else
        # Docker est là mais injoignable : démon arrêté ou utilisateur hors du groupe
        echo -e "  ${BOLD}⚠  Docker est installé mais injoignable${NC} (démon arrêté ou droits manquants)."
        if [ -n "$SUDO" ]; then
            $SUDO systemctl start docker 2>/dev/null || $SUDO service docker start 2>/dev/null || true
            groups "$USER" 2>/dev/null | grep -qw docker || $SUDO usermod -aG docker "$USER" 2>/dev/null || true
        fi
        if docker info &>/dev/null; then
            echo -e "  ${GREEN}✅ Docker démarré.${NC}"
        else
            echo -e "     Démarre le service : ${CYAN}sudo systemctl start docker${NC}"
            echo -e "     Ajoute-toi au groupe : ${CYAN}sudo usermod -aG docker \$USER${NC} (puis reconnecte-toi)."
            echo -e "     En attendant, le jeu marche en mode texte."
        fi
    fi
else
    docker_done=0
    if [ "$HAS_APT" = 1 ]; then
        if [ "${HQ_INSTALL_DOCKER:-0}" = 1 ]; then
            install_docker && docker_done=1
        elif [ -t 0 ]; then       # terminal interactif : on demande
            printf "\n  💻 Installer Docker pour jouer dans un vrai shell ? [o/N] "
            read -r rep
            case "$rep" in [oOyY]*) install_docker && docker_done=1 ;; esac
        fi
    fi
    if [ "$docker_done" = 1 ]; then
        echo -e "  ${GREEN}✅ Docker installé.${NC} ${BOLD}Déconnecte-toi / reconnecte-toi${NC} pour que le groupe docker prenne effet."
    else
        echo -e "\n  ${BOLD}💻 Optionnel :${NC} installe Docker pour jouer les missions dans un vrai shell :"
        echo -e "     sudo apt install docker.io && sudo usermod -aG docker \$USER"
        echo -e "     (puis déconnecte-toi / reconnecte-toi). Sans Docker, le jeu marche en mode texte."
        echo -e "     ${CYAN}Astuce :${NC} relance avec ${CYAN}HQ_INSTALL_DOCKER=1${NC} pour l'installer automatiquement."
    fi
fi

echo -e "\n  ${BOLD}C'est prêt !${NC} Quand tu veux jouer et apprendre, tape simplement :"
echo -e "  ${CYAN}${BOLD}hackquest${NC}"
if [ -n "$SHELL_RC" ]; then
    echo -e "\n  (dans ce terminal, active-le tout de suite avec : ${CYAN}source $SHELL_RC${NC})"
else
    echo -e "\n  (ouvre un nouveau terminal si la commande n'est pas encore trouvée)"
fi
echo
