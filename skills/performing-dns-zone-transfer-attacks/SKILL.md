---
name: performing-dns-zone-transfer-attacks
description: >-
  Enumerate DNS infrastructure by requesting full zone transfers (AXFR) from
  misconfigured authoritative DNS servers using dig, nslookup, and fierce.
  Covers zone transfer mechanics, subdomain harvesting, and identifying exposed
  internal hostnames in isolated lab environments.
domain: cybersecurity
subdomain: network-reconnaissance
tags: [dns, zone-transfer, axfr, enumeration, recon, network-security, beginner]
difficulty: beginner
version: "1.0.0"
author: RashpreetS01
license: Apache-2.0
mitre_techniques:
  - T1590.002
---

> **Educational Use Only** — All techniques described here must only be used in authorized, isolated lab environments. Never use against systems you do not own or have explicit written permission to test.

## When to Use

Use this skill during the reconnaissance phase of an authorized external or internal penetration test when the target operates its own DNS infrastructure. It is particularly valuable when passive DNS sources reveal few subdomains and active zone enumeration may be possible against misconfigured nameservers. It applies in CTF challenges where DNS hostnames contain hints or flags embedded in zone records.

## Prerequisites

- Docker and Docker Compose installed on the host machine
- Basic understanding of DNS record types (A, MX, NS, CNAME, TXT)
- Familiarity with how authoritative nameservers differ from recursive resolvers
- Lab: `labs/network/dns-zone-transfer` — start with `agentlab start dns-zone-transfer`

## Workflow

### Step 1: Start the Lab Environment

Launch the lab containing a misconfigured BIND9 authoritative nameserver for the fictional domain `lab.internal` that permits zone transfers from any source.

```bash
agentlab start dns-zone-transfer
# DNS server at 172.30.0.53, domain: lab.internal
# Attacker shell: agentlab exec dns-zone-transfer bash
```

### Step 2: Identify Authoritative Nameservers

Query for NS records to discover which servers are authoritative for the target domain before attempting transfers.

```bash
# Identify nameservers for the target domain
dig NS lab.internal @172.30.0.53

# Cross-verify with nslookup
nslookup -type=NS lab.internal 172.30.0.53
```

### Step 3: Attempt Zone Transfer with dig

Request the full zone transfer (AXFR) directly from the authoritative nameserver.

```bash
# AXFR zone transfer request
dig AXFR lab.internal @172.30.0.53

# Save output for offline analysis
dig AXFR lab.internal @172.30.0.53 > /tmp/zone_dump.txt
cat /tmp/zone_dump.txt
```

### Step 4: Attempt Zone Transfer with nslookup

Use nslookup as an alternative to verify and capture records in a different format.

```bash
nslookup
> server 172.30.0.53
> set type=any
> ls -d lab.internal
> exit
```

### Step 5: Use fierce for Automated Enumeration

Run fierce to combine zone transfer attempts with brute-force subdomain guessing in a single workflow.

```bash
fierce --domain lab.internal --dns-servers 172.30.0.53 --output /tmp/fierce_results.txt
cat /tmp/fierce_results.txt
```

### Step 6: Verify Results

Parse discovered hostnames for internal services and locate the flag embedded in zone records.

```bash
# Search for flag in TXT records or hostnames
grep -i "flag\|FLAG" /tmp/zone_dump.txt

agentlab verify dns-zone-transfer "FLAG{...}"
```

## Key Concepts

- **DNS Zone Transfer (AXFR)**: A DNS query type that requests a complete copy of all DNS records for a zone from an authoritative server — intended for replication between primary and secondary nameservers.
- **Authoritative Nameserver**: The DNS server that holds the definitive records for a domain zone and responds authoritatively to queries for that zone.
- **Zone Enumeration**: The process of discovering all hostnames, IP mappings, and service records within a DNS zone, revealing the full network topology of the target.
- **IXFR (Incremental Zone Transfer)**: A variant that transfers only changed records since a given serial number — less common but equally exploitable when unrestricted.
- **Mitigation**: Restrict AXFR transfers to known secondary nameserver IP addresses using ACLs in BIND (`allow-transfer { <trusted-ip>; };`).

## Tools

| Tool | Purpose | Install |
|------|---------|---------|
| `dig` | Primary DNS query tool supporting AXFR zone transfers | `apt install dnsutils` |
| `nslookup` | Interactive DNS lookup client | `apt install dnsutils` |
| `fierce` | Automated DNS enumeration combining AXFR and brute-force | `pip install fierce` |
| `dnsx` | Fast DNS toolkit for bulk record resolution | `go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest` |

## Output

On success, you should observe:
- A full list of DNS records (A, MX, CNAME, TXT, PTR) returned by the AXFR query
- Internal hostnames and IP addresses for services not publicly advertised
- TXT records containing configuration hints or embedded flags
- Flag captured in the format `FLAG{...}`

---

*All labs referenced in this skill run in isolated Docker environments with `internal: true` networks. No internet access. Educational use in authorized environments only.*
