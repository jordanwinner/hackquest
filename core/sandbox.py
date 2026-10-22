"""
Bac à sable : un vrai shell dans un conteneur Docker jetable.

Chaque mission « labo » démarre un conteneur neuf à partir de l'image
hackquest-lab (lab/Dockerfile + lab/world.py) :
- pas de réseau, utilisateur non-root, pas d'élévation de privilèges ;
- un seul shell bash persistant par mission, donc `cd`, les variables et les
  fichiers créés restent d'une commande à l'autre ;
- le conteneur est détruit à la fin de la mission (ou à la sortie du jeu).
"""
import atexit
import hashlib
import os
import re
import select
import shutil
import subprocess
import time
import uuid

LAB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lab")
HOME = "/home/hacker"
LABEL = "hackquest-lab=1"
DEFAULT_TIMEOUT = 10
MAX_SHOWN = 300  # lignes affichées par commande (la vérification voit tout)


def image_tag():
    """Le tag change dès que le Dockerfile ou le monde changent : l'image est alors reconstruite.
    HACKQUEST_LAB_IMAGE permet d'imposer une autre image (développement, tests)."""
    if os.environ.get("HACKQUEST_LAB_IMAGE"):
        return os.environ["HACKQUEST_LAB_IMAGE"]
    digest = hashlib.sha256()
    for name in ("Dockerfile", "world.py"):
        with open(os.path.join(LAB_DIR, name), "rb") as f:
            digest.update(f.read())
    return f"hackquest-lab:{digest.hexdigest()[:12]}"


def _docker(*args, **kwargs):
    try:
        return subprocess.run(["docker", *args], capture_output=True, text=True, **kwargs)
    except (FileNotFoundError, subprocess.SubprocessError):
        # Docker absent ou injoignable : on renvoie un échec propre (utile à l'exit)
        return subprocess.CompletedProcess(args, returncode=1, stdout="", stderr="")


_available = None


def docker_available(on_msg=lambda s: None):
    """True si Docker est utilisable (installé et le service répond).
    Le jeu ne touche pas au service Docker : le conteneur du labo, lui, est
    créé le temps d'une mission et détruit juste après (voir Lab.close)."""
    global _available
    if _available is None:
        _available = bool(shutil.which("docker")) and _docker("info", timeout=15).returncode == 0
    return _available


def image_ready():
    return _docker("image", "inspect", image_tag()).returncode == 0


def build_image(on_line=print):
    """Construit l'image (une seule fois). Renvoie True si tout s'est bien passé."""
    proc = subprocess.Popen(["docker", "build", "-t", image_tag(), LAB_DIR],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        on_line(line.rstrip())
    return proc.wait() == 0


def cleanup_stale():
    """Supprime les conteneurs oubliés par une partie précédente (crash, kill...)."""
    ids = _docker("ps", "-aq", "--filter", f"label={LABEL}").stdout.split()
    if ids:
        _docker("rm", "-f", *ids)


# Le shell n'a pas de vrai terminal : sa sortie arrive dans un pipe. Pour que `ls` et `grep`
# s'affichent comme dans un terminal (colonnes, couleurs) sans changer leur comportement
# dans un pipe (`ls | wc -l`), on compare leur sortie à celle du shell principal :
# identique = elle va à l'écran.
SHELL_INIT = r"""
export COLUMNS=@COLUMNS@ LANG=C.UTF-8
eval "$(dircolors -b)"
__hq_tty() { [ /proc/$BASHPID/fd/1 -ef /proc/$$/fd/1 ]; }
ls()   { if __hq_tty; then command ls -C --color=always "$@"; else command ls "$@"; fi; }
grep() { if __hq_tty; then command grep --color=always "$@"; else command grep "$@"; fi; }
"""
ANSI = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")
KILLED = re.compile(r"^bash: +\d+ Killed ")
BASH_LINE = re.compile(r"^bash: line \d+: ")  # « bash: line 4: tree: command not found » → « bash: tree: ... »


class ShellError(Exception):
    pass


class Lab:
    def __init__(self, spec):
        self.spec = spec
        self.name = f"hq-lab-{uuid.uuid4().hex[:8]}"
        self.shell = None
        self.shell_pid = None
        self.cwd = spec.get("cwd", HOME)
        self.timeout = spec.get("timeout", DEFAULT_TIMEOUT)
        self.marker = f"__HQ_{uuid.uuid4().hex}__"

    # ── cycle de vie ─────────────────────────────────────────────────────
    def start(self):
        res = _docker(
            "run", "-d", "--rm", "--name", self.name, "--label", LABEL,
            "--network", "none", "--hostname", "srv-target",
            "--security-opt", "no-new-privileges",
            "--memory", "256m", "--pids-limit", "256", "--cpus", "1",
            image_tag(),
        )
        if res.returncode != 0:
            raise ShellError(res.stderr.strip() or "docker run a échoué")
        atexit.register(self.close)
        # repère temporel pour les tests « fichier créé pendant la mission »
        self._exec_root("mkdir -p /run/hq && touch /run/hq/start")
        if self.spec.get("setup_root"):
            self._exec_root(self.spec["setup_root"])
        if self.spec.get("setup"):
            _docker("exec", "-u", "hacker", "-w", HOME, self.name, "bash", "-c", self.spec["setup"])
        if self.spec.get("background"):
            _docker("exec", "-d", "-u", "root", self.name, "bash", "-c", self.spec["background"])
        self._open_shell()

    def _exec_root(self, script):
        return _docker("exec", "-u", "root", self.name, "bash", "-c", script)

    def _open_shell(self):
        env_flags = []
        for key, val in self.spec.get("env", {}).items():
            env_flags += ["-e", f"{key}={val}"]
        self.shell = subprocess.Popen(
            ["docker", "exec", "-i", "-u", "hacker", "-w", self.cwd,
             "-e", f"HOME={HOME}", "-e", "USER=hacker", "-e", "TERM=xterm-256color",
             *env_flags,
             self.name, "bash", "--noprofile", "--norc"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0,
            # nouvelle session : le Ctrl+C du joueur ne doit pas tuer `docker exec`, c'est nous qui gérons
            start_new_session=True,
        )
        self._reset_reader()
        self._send(SHELL_INIT.replace("@COLUMNS@", str(shutil.get_terminal_size().columns)))
        self._send(f"echo {self.marker}$$\n")
        _, pid = self._read_until_marker(10, echo=False)
        self.shell_pid = pid.strip() or None

    def close(self):
        if self.shell:
            try:
                self.shell.kill()
            except OSError:
                pass
            self.shell = None
        _docker("rm", "-f", self.name)

    def reset(self):
        self.close()
        self.__init__(self.spec)
        self.start()

    # ── exécution ────────────────────────────────────────────────────────
    def _send(self, text):
        try:
            self.shell.stdin.write(text.encode())
        except (BrokenPipeError, OSError):
            raise ShellError("le shell s'est fermé")

    def _reset_reader(self):
        self._buf, self._lines, self._held = "", [], None

    def _read_until_marker(self, timeout, echo=True):
        """Lit la sortie jusqu'au marqueur de fin. Renvoie (sortie, reste_après_marqueur).
        Affiche les lignes au fil de l'eau avec une ligne de retard : la dernière
        ligne retenue est le saut de ligne ajouté par nous, qu'on ne doit pas montrer.
        L'état de lecture est gardé dans l'objet : après une interruption, on reprend
        sans perdre ce qui a déjà été lu (utile pour `tail -f`)."""
        fd = self.shell.stdout.fileno()
        deadline = time.monotonic() + timeout
        while True:
            while "\n" in self._buf:
                line, self._buf = self._buf.split("\n", 1)
                if line.startswith(self.marker):
                    if self._held:  # sortie sans saut de ligne final : c'est du vrai contenu
                        self._emit(self._held, echo)
                    out = "\n".join(self._lines)
                    self._reset_reader()
                    return out, line[len(self.marker):]
                if self._held is not None:
                    self._emit(self._held, echo)
                self._held = line
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError
            ready, _, _ = select.select([fd], [], [], min(remaining, 0.2))
            if not ready:
                continue
            chunk = os.read(fd, 65536)
            if not chunk:
                raise ShellError("le shell s'est fermé")
            self._buf += chunk.decode(errors="replace")

    def _emit(self, line, echo):
        line = BASH_LINE.sub("bash: ", line)
        if KILLED.match(line):  # bruit laissé par l'arrêt d'une commande trop longue
            return
        self._lines.append(ANSI.sub("", line))  # la vérification travaille sur le texte brut
        if echo and len(self._lines) <= MAX_SHOWN:
            print(line)
        elif echo and len(self._lines) == MAX_SHOWN + 1:
            print(f"\033[2m  … sortie tronquée à l'écran ({MAX_SHOWN} lignes) — ajoute | head ou | less\033[0m")

    def _kill_children(self):
        if self.shell_pid:
            # tous les processus du joueur sauf son shell (sans dépendre de procps)
            self._exec_root("for d in /proc/[0-9]*; do p=${d#/proc/}; "
                            f'[ "$(stat -c %U $d)" = hacker ] && [ $p != {self.shell_pid} ] && kill -9 $p; '
                            "done 2>/dev/null")

    def run(self, command, echo=True, timeout=None):
        """Exécute une commande dans le shell persistant.
        Renvoie (code_retour, sortie, interrompue)."""
        # stdin fermé : une commande qui attend une saisie (cat sans argument...) ne bloque pas le shell
        self._reset_reader()
        self._send(f"{{ {command}\n}} </dev/null 2>&1; __hq=$?; echo; echo \"{self.marker}$__hq:$PWD\"\n")
        interrupted = False
        try:
            out, tail = self._read_until_marker(timeout or self.timeout, echo)
        except (TimeoutError, KeyboardInterrupt):
            interrupted = True
            self._kill_children()
            try:
                out, tail = self._read_until_marker(3, echo)
            except (TimeoutError, KeyboardInterrupt):
                self._restart_shell()
                return 130, "", True
        except ShellError:
            # `exit` tape par le joueur : on rouvre un shell au même endroit
            self._restart_shell()
            return 0, "", False
        code, _, cwd = tail.partition(":")
        self.cwd = cwd or self.cwd
        return int(code) if code.isdigit() else 1, out, interrupted

    def _restart_shell(self):
        if self.shell:
            self.shell.kill()
        self._open_shell()

    # ── vérification de l'objectif ──────────────────────────────────────
    def _hidden(self, script):
        """Lance un script de vérification dans un sous-shell (même dossier, mêmes variables)."""
        code, out, _ = self.run(f"( {script} )", echo=False, timeout=15)
        return code, out

    def check(self, output, code):
        """L'objectif est atteint si au moins une des alternatives de `checks` est remplie.
        Sans `checks`, il suffit que la commande ait réussi (code 0)."""
        alternatives = self.spec.get("checks")
        if not alternatives:
            return code == 0
        return any(self._check_one(alt, output) for alt in alternatives)

    def _check_one(self, c, output):
        listify = lambda v: v if isinstance(v, list) else [v]
        if any(s not in output for s in listify(c.get("out", []))):
            return False
        if any(s in output for s in listify(c.get("not_out", []))):
            return False
        if "re" in c and not re.search(c["re"], output, re.M):
            return False
        if "lines" in c and len([l for l in output.splitlines() if l.strip()]) != c["lines"]:
            return False
        if "same_as" in c:
            _, expected = self._hidden(c["same_as"])
            if not expected.strip() or expected.strip() not in output.strip():
                return False
        if "test" in c and self._hidden(c["test"])[0] != 0:
            return False
        return True

    def prompt_path(self):
        return "~" + self.cwd[len(HOME):] if self.cwd.startswith(HOME) else self.cwd


def incomplete(command):
    """True si la commande n'est pas finie (guillemet ouvert, heredoc, `if` sans `fi`...).
    bash -n ne fait qu'analyser la syntaxe : rien n'est exécuté sur la machine du joueur."""
    res = subprocess.run(["bash", "-n", "-c", command], capture_output=True, text=True)
    err = res.stderr
    return "unexpected end of file" in err or "here-document" in err
