# Le serveur d'entraînement de HackQuest : un faux serveur « compromis »
# où les commandes du joueur s'exécutent pour de vrai, sans réseau.
#
# Tout tourne en boucle locale (127.0.0.1) : les services réseau (web, ssh, dns)
# sont démarrés le temps d'une mission, donc nmap/curl/ssh/john fonctionnent
# réellement sans que le conteneur n'ait jamais accès à Internet.
# Image figée en linux/amd64 : les binaires fournis (crackme, vuln) et les
# adresses des missions PWN sont x86-64, donc on force cette architecture pour
# un comportement identique partout — y compris sur Mac Apple Silicon (Docker
# Desktop l'émule : 1re construction plus longue, mais elle réussit).
FROM --platform=linux/amd64 python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
# résistance aux coupures réseau pendant l'installation des paquets
RUN printf 'Acquire::Retries "8";\nAcquire::http::Timeout "30";\n' > /etc/apt/apt.conf.d/80-hq-retries
RUN for i in 1 2 3; do apt-get update && break || sleep 5; done \
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
COPY bin/vuln /opt/vuln
COPY world.py /tmp/world.py
RUN python3 /tmp/world.py && rm /tmp/world.py \
 && updatedb && chmod 0644 /var/lib/plocate/plocate.db \
 && ssh-keygen -A

ENV LANG=C.UTF-8
CMD ["sleep", "infinity"]
