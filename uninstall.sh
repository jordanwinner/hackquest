#!/usr/bin/env bash
# HackQuest — désinstallation.
# Retire la commande, les lignes PATH ajoutées, les conteneurs et l'image Docker.
# Garde ta progression par défaut ; --purge l'efface aussi.
#   ./uninstall.sh [--purge]
set -u

PURGE=0
[ "${1:-}" = "--purge" ] && PURGE=1

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[0;33m'; BOLD='\033[1m'; NC='\033[0m'
ok()   { printf "  ${GREEN}✅ %s${NC}\n" "$*"; }
info() { printf "  ${CYAN}•  %s${NC}\n" "$*"; }

GAME_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
BIN="$HOME/.local/bin/hackquest"

printf "\n  ${BOLD}Désinstallation de HackQuest${NC}\n\n"

# ── commande
if [ -L "$BIN" ] || [ -f "$BIN" ]; then
    rm -f "$BIN"; ok "commande 'hackquest' retirée de ~/.local/bin"
fi

# ── lignes PATH ajoutées par l'installeur (on ne touche qu'à notre bloc)
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
    if [ -f "$rc" ] && grep -q "# ajouté par HackQuest" "$rc"; then
        sed -i '/# ajouté par HackQuest/,+1d' "$rc"
        ok "ligne PATH retirée de $rc"
    fi
done

# ── Docker : conteneurs du labo + image(s)
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    cids=$(docker ps -aq --filter label=hackquest-lab=1 2>/dev/null)
    [ -n "$cids" ] && docker rm -f $cids >/dev/null 2>&1 && ok "conteneurs du labo supprimés"
    imgs=$(docker images -q hackquest-lab 2>/dev/null | sort -u)
    if [ -n "$imgs" ]; then
        docker rmi -f $imgs >/dev/null 2>&1 && ok "image Docker du labo supprimée (~670 Mo libérés)"
    else
        info "aucune image de labo à supprimer"
    fi
else
    info "Docker indisponible : si l'image existe, retire-la avec 'docker rmi hackquest-lab'"
fi

# ── progression
if [ "$PURGE" = 1 ]; then
    rm -f "$HOME/.hackquest_save.json" "$HOME/.hackquest_save.json.bak"
    ok "progression effacée (--purge)"
elif [ -f "$HOME/.hackquest_save.json" ]; then
    info "progression gardée dans ~/.hackquest_save.json (efface-la avec --purge)"
fi

# ── dossier du jeu (ce dossier) : supprimé en dernier
printf "\n  ${YELLOW}Supprimer aussi le dossier du jeu ($GAME_DIR) ? [o/N]${NC} "
read -r ans
case "${ans:-n}" in
    o|O|oui|y|Y)
        cd "$HOME" || exit 0
        rm -rf "$GAME_DIR"
        ok "dossier du jeu supprimé"
        ;;
    *)
        info "dossier gardé : $GAME_DIR"
        ;;
esac

printf "\n  ${BOLD}HackQuest désinstallé.${NC} Ouvre un nouveau terminal pour rafraîchir le PATH.\n\n"
