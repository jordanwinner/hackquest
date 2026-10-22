# Le serveur d'entraînement de HackQuest : un faux serveur « compromis »
# où les commandes du joueur s'exécutent pour de vrai, sans réseau.
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      procps psmisc tree file less xxd binutils plocate zip unzip bc \
      p7zip-full openssl rsync cron \
      libimage-exiftool-perl binwalk steghide foremost tshark yara \
      strace ltrace gdb checksec \
 && rm -rf /var/lib/apt/lists/*

COPY bin/crackme /opt/crackme
COPY world.py /tmp/world.py
RUN python3 /tmp/world.py && rm /tmp/world.py && updatedb

ENV LANG=C.UTF-8
CMD ["sleep", "infinity"]
