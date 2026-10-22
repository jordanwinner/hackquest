# Le serveur d'entraînement de HackQuest : un faux serveur « compromis »
# où les commandes du joueur s'exécutent pour de vrai, sans réseau.
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      procps psmisc tree file less xxd binutils plocate zip unzip bc \
 && rm -rf /var/lib/apt/lists/*

COPY world.py /tmp/world.py
RUN python3 /tmp/world.py && rm /tmp/world.py && updatedb

ENV LANG=C.UTF-8
CMD ["sleep", "infinity"]
