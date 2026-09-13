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

# ── Copier les fichiers
echo -e "  📁 Installation dans $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

# Si on est déjà dans le dossier du projet
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR/core"        "$INSTALL_DIR/"
cp    "$SCRIPT_DIR/hackquest.py" "$INSTALL_DIR/"

echo -e "  ${GREEN}✅ Fichiers copiés${NC}"

# ── Créer la commande hackquest dans ~/.local/bin
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/hackquest" << EOF
#!/usr/bin/env bash
cd "$INSTALL_DIR" && python3 hackquest.py "\$@"
EOF
chmod +x "$BIN_DIR/hackquest"

echo -e "  ${GREEN}✅ Commande 'hackquest' installée dans $BIN_DIR${NC}"

# ── Ajouter ~/.local/bin au PATH si pas déjà dedans
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "$BIN_DIR" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
        echo -e "  ${GREEN}✅ PATH mis à jour dans $SHELL_RC${NC}"
    fi
fi

# ── Test rapide
echo -e "\n  🧪 Test de démarrage..."
if python3 -c "
import sys
sys.path.insert(0, '$INSTALL_DIR')
from core.registry import count_total_missions
print(f'  {count_total_missions()} missions chargées')
" 2>/dev/null; then
    echo -e "\n${GREEN}${BOLD}  ✅ HackQuest installé avec succès !${NC}"
else
    echo -e "\n${RED}  ❌ Erreur lors du test. Vérifie les fichiers.${NC}"
    exit 1
fi

echo -e "\n  Pour lancer le jeu :"
echo -e "  ${CYAN}${BOLD}  source $SHELL_RC && hackquest${NC}\n"
