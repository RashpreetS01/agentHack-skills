---
name: performing-port-scanning-in-safe-lab
description: >-
  Perform TCP and UDP port scanning against isolated lab targets using Nmap to
  discover open services, identify running software versions, and enumerate the
  attack surface. Covers SYN scans, version detection, and OS fingerprinting
  techniques exclusively in controlled Docker lab environments.
domain: cybersecurity
subdomain: network-reconnaissance
tags: [nmap, port-scanning, network-recon, beginner, service-enumeration, tcp-udp]
difficulty: beginner
mitre_techniques: [T1046, T1595.001]
nist_csf_functions: [Identify]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/network/port-scan-lab
---

> ⚠️ **Educational Use Only** — Port scanning without authorization is illegal in many jurisdictions and violates terms of service for most networks. Practice exclusively in the provided lab environment. Never scan IP addresses or networks you do not own or have explicit written permission to scan.

## When to Use

- During the reconnaissance phase of an authorized penetration test to map open services
- In CTF challenges requiring initial enumeration of a target machine
- When learning Nmap syntax, scan types, and output interpretation
- As a prerequisite for service-specific exploitation skills (e.g., exploiting an exposed SMB port)
- When validating firewall rules — confirming that only expected ports are reachable

## Prerequisites

- **Software:** Docker + Docker Compose (lab uses pre-installed Nmap)
- **Knowledge:** Basic TCP/IP concepts (what a port is, what TCP handshakes look like)
- **Lab:** `labs/network/port-scan-lab` — start with `agentlab start port-scan-lab`
- **Difficulty:** Beginner
- **Time:** 20–35 minutes

## Workflow

### Step 1: Start the Lab

```bash
agentlab start port-scan-lab
agentlab exec port-scan-lab bash
# You are now inside the attacker container
# Target IP: 172.20.0.2 (visible only inside the lab network)
```

### Step 2: Basic TCP Connect Scan

Start with a fast scan of the most common 1000 ports:

```bash
nmap 172.20.0.2
```

This performs a TCP connect scan. Observe open ports in the output.

### Step 3: SYN (Stealth) Scan

A SYN scan is faster and less detectable than a full connect scan:

```bash
# Requires root/sudo inside the attacker container
nmap -sS 172.20.0.2
```

SYN scan sends a SYN, receives SYN-ACK (open) or RST (closed), and never completes the handshake.

### Step 4: Full Port Scan

The default scan only covers 1000 ports. Scan all 65535:

```bash
nmap -p- 172.20.0.2
# Faster version with reduced timing
nmap -p- --min-rate=1000 172.20.0.2
```

### Step 5: Service and Version Detection

Once open ports are known, identify what software is running:

```bash
nmap -sV -p 22,80,443,8080 172.20.0.2
```

`-sV` sends probe packets to each open port to determine service name and version. Look for version numbers that may indicate outdated, vulnerable software.

### Step 6: OS Fingerprinting

Attempt to determine the operating system of the target:

```bash
nmap -O 172.20.0.2
```

Nmap compares TCP/IP stack behavior against a fingerprint database to estimate the OS. Useful for understanding the target environment.

### Step 7: Comprehensive Enumeration Scan

Combine common options for a thorough enumeration scan:

```bash
nmap -sV -sC -O -p- --open -oN scan_results.txt 172.20.0.2
```

Options:
- `-sC` — run default NSE scripts (safe enumeration scripts)
- `--open` — only show open ports
- `-oN scan_results.txt` — save output to file

### Step 8: UDP Scan

Many services run on UDP (DNS:53, SNMP:161, DHCP:67). UDP scans are slower:

```bash
nmap -sU --top-ports=20 172.20.0.2
```

### Step 9: Capture the Flag

A hidden service is listening on a non-standard port. Find it and retrieve the flag:

```bash
nmap -p- 172.20.0.2 | grep open
# Connect to the hidden service
nc 172.20.0.2 <hidden-port>
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| TCP SYN Scan | Half-open scan — sends SYN, receives SYN-ACK (open) or RST (closed), RST sent immediately |
| TCP Connect Scan | Full 3-way handshake — more detectable but doesn't require root |
| Port States | Open (service listening), Closed (no service, port reachable), Filtered (firewall dropping packets) |
| Service Banner | Version string a service sends on connection, used by Nmap -sV |
| NSE Scripts | Nmap Scripting Engine — Lua scripts that perform enumeration, vulnerability checks, and exploitation |
| T1046 | MITRE ATT&CK: Network Service Discovery |
| T1595.001 | MITRE ATT&CK: Active Scanning — Scanning IP Blocks |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `nmap` | Port scanning, service detection, OS fingerprinting | ✅ Pre-installed |
| `nc` / `netcat` | Manual connection to discovered services | ✅ Pre-installed |
| `masscan` | Ultra-fast port scanner for large IP ranges | ✅ Pre-installed |
| `rustscan` | Fast Rust-based port scanner | ✅ Pre-installed |

## Common Scenarios

### Scenario 1: Initial Enumeration of a CTF Machine

```bash
# Phase 1: fast scan to find open ports
nmap -p- --min-rate=5000 172.20.0.2 -oN ports.txt

# Phase 2: targeted version scan on open ports only
ports=$(grep ^[0-9] ports.txt | cut -d '/' -f 1 | tr '\n' ',' | sed 's/,$//')
nmap -sV -sC -p "$ports" 172.20.0.2 -oN services.txt
```

This two-phase approach is faster than running full version detection across all 65535 ports at once.

### Scenario 2: Firewall Validation

```bash
# Scan from outside the expected subnet
nmap -sS --source-port 53 172.20.0.2
# Some firewalls allow traffic from source port 53 (DNS)
```

### Scenario 3: Finding Hidden Management Ports

```bash
# Common non-standard management ports
nmap -p 8080,8443,8888,9090,9200,27017,6379,5432,3306 -sV 172.20.0.2
```

## Output / Verification

```bash
agentlab verify port-scan-lab "FLAG{hidden_service_found}"
```

**Score:** 50 points for finding all open ports + 100 points for connecting to the hidden service and retrieving the flag

## Further Reading

- [Nmap Reference Guide](https://nmap.org/book/man.html)
- [OWASP Testing: Network Infrastructure Configuration](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/01-Conduct_Search_Engine_Discovery_Reconnaissance_for_Information_Leakage)
- MITRE ATT&CK: [T1046](https://attack.mitre.org/techniques/T1046/) | [T1595.001](https://attack.mitre.org/techniques/T1595/001/)
