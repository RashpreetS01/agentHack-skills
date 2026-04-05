# AgentHack-Skills — SUID Lab Target
# ⚠️ Educational Use Only — Purpose-built vulnerable container

FROM ubuntu:22.04

# Suppress interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install tools
RUN apt-get update && apt-get install -y \
    find \
    python3 \
    vim \
    less \
    bash \
    curl \
    wget \
    sudo \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

# Create non-privileged user (student starts here)
RUN useradd -m -s /bin/bash www-data-student && \
    echo "www-data-student:student123" | chpasswd

# Plant the flag (only readable by root)
RUN echo "FLAG{suid_privesc_complete}" > /root/flag.txt && \
    chmod 600 /root/flag.txt

# Create intentional SUID misconfigurations (EDUCATIONAL PURPOSE)
# This mimics real-world misconfigurations students will encounter
RUN chmod u+s /usr/bin/python3.10 && \
    chmod u+s /usr/bin/find && \
    chmod u+s /usr/bin/vim.basic 2>/dev/null || true

# Add a LinPEAS copy for students who want to automate enumeration
RUN mkdir -p /opt/tools && \
    echo '#!/bin/bash\necho "LinPEAS simulation — enumerate SUID: find / -perm -u=s -type f 2>/dev/null"' > /opt/tools/linpeas.sh && \
    chmod +x /opt/tools/linpeas.sh

# SSH for direct access
RUN mkdir /run/sshd && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
