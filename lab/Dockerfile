# Le serveur d'entraînement de HackQuest : un faux serveur « compromis »
# où les commandes du joueur s'exécutent pour de vrai, sans réseau.
#
# Tout tourne en boucle locale (127.0.0.1) : les services réseau (web, ssh, dns)
# sont démarrés le temps d'une mission, donc nmap/curl/ssh/john fonctionnent
# réellement sans que le conteneur n'ait jamais accès à Internet.
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      procps psmisc tree file less xxd binutils plocate zip unzip bc \
      p7zip-full openssl rsync cron \
      libimage-exiftool-perl binwalk steghide foremost tshark yara \
      strace ltrace gdb checksec \
      nmap iproute2 iputils-ping traceroute netcat-openbsd curl wget \
      openssh-server openssh-client dnsmasq bind9-dnsutils bind9-host \
      gobuster ffuf dirb sqlmap john hashid fcrackzip \
 && rm -rf /var/lib/apt/lists/*

COPY bin/crackme /opt/crackme
COPY world.py /tmp/world.py
RUN python3 /tmp/world.py && rm /tmp/world.py \
 && updatedb && chmod 0644 /var/lib/plocate/plocate.db \
 && ssh-keygen -A

ENV LANG=C.UTF-8
CMD ["sleep", "infinity"]
