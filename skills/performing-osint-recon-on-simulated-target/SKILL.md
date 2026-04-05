---
name: performing-osint-recon-on-simulated-target
description: >-
  Conduct Open Source Intelligence (OSINT) reconnaissance on a simulated target
  organization using public information sources, DNS enumeration, certificate
  transparency logs, and Google dorks. All reconnaissance is performed against
  a fully simulated, consent-given lab target with no real personal data involved.
domain: cybersecurity
subdomain: osint-reconnaissance
tags: [osint, reconnaissance, dns-enumeration, google-dorks, beginner, information-gathering]
difficulty: beginner
mitre_techniques: [T1589, T1590, T1591, T1596]
nist_csf_functions: [Identify]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/network/port-scan-lab
---

> ⚠️ **Educational Use Only** — All OSINT in this skill is practiced against simulated, fictitious targets. Never collect personal information about real individuals without consent. OSINT techniques applied to real people without their knowledge may violate privacy laws (GDPR, CCPA) even when using public data. Professional OSINT is conducted with clear scope agreements.

## When to Use

- At the start of an authorized penetration test, during the passive reconnaissance phase
- In CTF challenges requiring information gathering before exploitation
- When learning how attackers gather intelligence before targeting an organization
- When training a security team to understand their own exposure footprint
- As a prerequisite for spear-phishing simulations, credential stuffing, and targeted attack simulation skills

## Prerequisites

- **Knowledge:** Basic internet navigation, understanding of DNS (what an A record, MX record, and CNAME are)
- **Lab:** `labs/network/port-scan-lab` (shared environment with simulated DNS)
- **Difficulty:** Beginner — no technical background required
- **Time:** 30–45 minutes

## Workflow

### Step 1: Start the Lab

```bash
agentlab start port-scan-lab
# The lab includes a simulated DNS server and fake company profile for "Acme Corp"
# All data is synthetic — no real organizations or individuals
agentlab exec port-scan-lab bash
```

### Step 2: DNS Enumeration

DNS records reveal infrastructure:

```bash
# Basic DNS lookup (against simulated DNS server)
dig acme-corp.lab A          # IPv4 addresses
dig acme-corp.lab MX         # Mail servers
dig acme-corp.lab NS         # Name servers
dig acme-corp.lab TXT        # SPF, DKIM, verification records
dig acme-corp.lab AAAA       # IPv6 addresses

# Zone transfer (misconfiguration — dumps all DNS records)
dig axfr acme-corp.lab @ns1.acme-corp.lab
```

### Step 3: Subdomain Enumeration

```bash
# Dictionary-based subdomain enumeration
gobuster dns -d acme-corp.lab \
  -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -r 172.20.0.10:53

# Alternative with ffuf
ffuf -u http://FUZZ.acme-corp.lab \
     -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
     -mc 200,301

# Discovered subdomains hint at internal services:
# mail.acme-corp.lab, dev.acme-corp.lab, staging.acme-corp.lab
```

### Step 4: Certificate Transparency Log Simulation

In real OSINT, certificate transparency logs reveal all subdomains that have ever had TLS certificates:

```bash
# Lab simulates crt.sh response for acme-corp.lab
curl http://crt-sim.lab/acme-corp.lab | jq '.[].name_value' | sort -u

# Common finds: internal subdomains leaked via certificates
# vpn.acme-corp.lab, jira.acme-corp.lab, confluence.acme-corp.lab
```

### Step 5: Email Harvesting Simulation

```bash
# Simulated theHarvester output for acme-corp.lab
theHarvester -d acme-corp.lab -b lab-sim -l 50

# Output includes simulated email format:
# j.smith@acme-corp.com, a.jones@acme-corp.com
# Pattern: firstname.lastname@acme-corp.com
```

This reveals the email format — critical for spear-phishing and credential stuffing.

### Step 6: Google Dork Simulation

Google dorks find sensitive files indexed by search engines:

```bash
# The lab provides a simulated search engine with indexed target pages
dork-sim "site:acme-corp.lab filetype:pdf"
dork-sim "site:acme-corp.lab inurl:admin"
dork-sim "site:acme-corp.lab intitle:\"index of\""
dork-sim "\"acme-corp.lab\" filetype:sql"

# Results may include: employee_list.pdf, admin/login.php, database_backup.sql
```

### Step 7: Capture the Flag

The simulated zone transfer exposes a flag record:

```bash
dig axfr acme-corp.lab @ns1.acme-corp.lab | grep FLAG
# flag.acme-corp.lab.  300 IN TXT "FLAG{dns_zone_transfer_exposed}"
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| OSINT | Open Source Intelligence — gathering intelligence from publicly available sources |
| DNS Zone Transfer | AXFR request that dumps all DNS records — should be restricted to authorized secondaries only |
| Certificate Transparency | Public logs of all TLS certificates issued, revealing hostnames |
| Google Dork | Advanced search operator to find specific file types or exposed content |
| T1589 | MITRE ATT&CK: Gather Victim Identity Information |
| T1590 | MITRE ATT&CK: Gather Victim Network Information |
| T1596 | MITRE ATT&CK: Search Open Technical Databases |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `dig` | DNS query tool | ✅ Pre-installed |
| `gobuster dns` | Subdomain bruteforcing | ✅ Pre-installed |
| `theHarvester` | Email, name, subdomain harvesting | ✅ Pre-installed (lab-sim mode) |
| `whois` | Domain registration information | ✅ Pre-installed |

## Output / Verification

```bash
agentlab verify port-scan-lab "FLAG{dns_zone_transfer_exposed}"
```

## Further Reading

- [OSINT Framework](https://osintframework.com/)
- MITRE ATT&CK: [T1589](https://attack.mitre.org/techniques/T1589/) | [T1590](https://attack.mitre.org/techniques/T1590/)
- [Google Hacking Database (GHDB)](https://www.exploit-db.com/google-hacking-database)
- [theHarvester GitHub](https://github.com/laramies/theHarvester)
