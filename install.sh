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

echo -e "\n${CYAN}${BOLD}"
echo "  ██╗  ██╗ █████╗  ██████╗██╗  ██╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗"
echo "  ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝"
echo "  ███████║███████║██║     █████╔╝ ██║   ██║██║   ██║█████╗  ███████╗   ██║   "
echo "  ██╔══██║██╔══██║██║     ██╔═██╗ ██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║   "
echo "  ██║  ██║██║  ██║╚██████╗██║  ██╗╚██████╔╝╚██████╔╝███████╗███████║   ██║   "
echo "  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚══▀▀╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝   "
echo -e "${NC}"
echo -e "  ${BOLD}Installation de HackQuest${NC}\n"

# ── Vérifier Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ Python 3 est requis. Installe-le avec : sudo apt install python3${NC}"
    exit 1
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
    command -v git &>/dev/null || { echo -e "${RED}❌ git est requis : sudo apt install git${NC}"; exit 1; }
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

# ── Créer la commande hackquest dans ~/.local/bin
mkdir -p "$BIN_DIR"
chmod +x "$GAME_DIR/hackquest"
ln -sf "$GAME_DIR/hackquest" "$BIN_DIR/hackquest"

echo -e "  ${GREEN}✅ Commande 'hackquest' installée dans $BIN_DIR${NC}"

# ── Ajouter ~/.local/bin au PATH si pas déjà dedans
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    # la ligne écrite contient « $HOME » littéralement : on cherche les deux formes
    if ! grep -qF -e "$BIN_DIR" -e '$HOME/.local/bin' "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
        echo -e "  ${GREEN}✅ PATH mis à jour dans $SHELL_RC${NC}"
    fi
fi

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
if command -v docker &>/dev/null && docker info &>/dev/null; then
    echo -e "  ${GREEN}✅ Docker détecté : les missions 💻 se joueront dans un vrai shell${NC}"
else
    echo -e "\n  ${BOLD}💻 Optionnel :${NC} installe Docker pour jouer les missions dans un vrai shell :"
    echo -e "     sudo apt install docker.io && sudo usermod -aG docker \$USER"
    echo -e "     (puis déconnecte-toi / reconnecte-toi). Sans Docker, le jeu marche en mode texte."
fi

echo -e "\n  Pour lancer le jeu :"
if [ -n "$SHELL_RC" ]; then
    echo -e "  ${CYAN}${BOLD}  source $SHELL_RC && hackquest${NC}\n"
else
    echo -e "  ${CYAN}${BOLD}  hackquest${NC}\n"
fi
