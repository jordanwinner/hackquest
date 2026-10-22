#!/usr/bin/env python3
"""
Joue chaque labo avec sa solution (doit réussir) puis avec une mauvaise commande
(doit échouer). Nécessite Docker et l'image du labo.

    python3 tests/test_labs.py            # tous les labos
    python3 tests/test_labs.py nav_ fil_  # seulement ceux dont l'id commence ainsi
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.labs import LABS
from core.registry import get_mission_by_id
from core.sandbox import Lab, docker_available, image_ready, image_tag
from core.validate import is_valid_answer

WRONG = "echo rien"


def passes(lab, mission, command):
    code, out, _ = lab.run(command, echo=False)
    return is_valid_answer(command, mission) and lab.check(out, code), out


def main(prefixes):
    if not docker_available() or not image_ready():
        sys.exit(f"Docker ou l'image {image_tag()} est indisponible.")
    failures = []
    for mid, spec in LABS.items():
        if prefixes and not mid.startswith(tuple(prefixes)):
            continue
        mission = get_mission_by_id(mid)
        lab = Lab(spec)
        try:
            lab.start()
            wrong, _ = passes(lab, mission, WRONG)
            ok, out = passes(lab, mission, spec["solution"])
        finally:
            lab.close()
        status = "ok" if ok and not wrong else "ÉCHEC"
        print(f"{status:5} {mid:8} {spec['solution']}")
        if status != "ok":
            failures.append(mid)
            print("      " + ("la mauvaise commande passe" if wrong else "sortie : " + out[-300:].replace("\n", " ⏎ ")))
    print(f"\n{len(failures)} échec(s)" + (f" : {', '.join(failures)}" if failures else ""))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
