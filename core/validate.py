"""
Validation des réponses du joueur.

L'ancien test (« le mot-clé apparaît quelque part ») acceptait n'importe quoi :
`false` validait `ls`, `echo cd` validait `cd`, `whoami` validait `id`...
Ici on distingue trois sortes de mots-clés :

- le nom de la commande attendue (`ls`, `cd`, `nmap --script vuln`) : il doit
  être en position de commande (début de ligne, après un pipe, un `;`, `sudo`...)
  et ne pas être collé à d'autres lettres (`lsblk` n'est pas `ls`) ;
- un nom d'outil isolé (`grep`, `secretsdump`) : il doit être un mot entier,
  éventuellement préfixé/suffixé par un tiret ou un chiffre
  (`impacket-secretsdump`, `proxychains4`) ;
- tout le reste (options, chemins, syntaxe) : présent tel quel, sans être collé
  à d'autres lettres de part et d'autre.
"""
import re

# mots qui lancent une autre commande : ce qui suit est aussi en position de commande
_PREFIXES = {"sudo", "time", "watch", "nohup", "exec", "env", "xargs", "nice",
             "strace", "ltrace", "proxychains", "proxychains4"}
_SEPARATORS = ("|", ";", "&", "(", "`", "{", "!")
_WORD = re.compile(r"^[a-z][\w.+-]*$")


def _norm(text):
    return " ".join(text.lower().split())


def _heads(expected_cmds):
    """Noms des commandes attendues (premier mot, hors sudo)."""
    heads = set()
    for cmd in expected_cmds:
        words = _norm(cmd).split()
        while words and words[0] in _PREFIXES:
            words = words[1:]
        if words and _WORD.match(words[0]):
            heads.add(words[0])
    return heads


def _in_command_position(text, start):
    before = text[:start].rstrip()
    if not before or before.endswith(_SEPARATORS):
        return True
    return before.split()[-1].lstrip("|;&(`{") in _PREFIXES


def _edge_ok(text, start, end, keyword):
    """Le mot-clé n'est pas collé à d'autres lettres/chiffres."""
    if keyword[0].isalnum() and start > 0 and (text[start - 1].isalnum() or text[start - 1] == "_"):
        return False
    if keyword[-1].isalnum() and end < len(text) and (text[end].isalnum() or text[end] == "_"):
        # une option peut être prolongée : `-lh` → `-lha`, `nmap -T` → `nmap -T4`
        if not keyword.split()[-1].startswith("-"):
            return False
    return True


def _find_all(text, keyword):
    start = text.find(keyword)
    while start != -1:
        yield start, start + len(keyword)
        start = text.find(keyword, start + 1)


def keyword_matches(user_input, keyword, heads=()):
    text, kw = _norm(user_input), _norm(keyword)
    if not kw:
        return False
    first = kw.split()[0]

    if first in heads:
        return any(_in_command_position(text, s) and _edge_ok(text, s, e, kw)
                   for s, e in _find_all(text, kw))

    if _WORD.match(kw):
        for token in re.split(r"[\s|;&()`'\"{}<>=,/]+", text):
            if token == kw or re.fullmatch(rf"(?:[\w.]+[-.])?{re.escape(kw)}(?:-[\w.-]+|\d+)?", token):
                return True
        return False

    return any(_edge_ok(text, s, e, kw) for s, e in _find_all(text, kw))


def is_valid_answer(user_input, mission):
    heads = _heads(mission.get("expected_cmd", []))
    # les commandes attendues comptent aussi (`unzip` pour une mission « zip et unzip »)
    keywords = list(mission.get("accept_contains", [])) + list(mission.get("expected_cmd", []))
    return any(keyword_matches(user_input, k, heads) for k in keywords)
