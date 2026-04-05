---
name: performing-web-directory-enumeration
description: >-
  Discover hidden directories, files, and endpoints on web servers using wordlist-based
  fuzzing with tools like ffuf, gobuster, and dirb inside isolated lab environments.
  Covers recursive enumeration, extension fuzzing, virtual host discovery, and
  filtering strategies for reducing noise in results.
domain: cybersecurity
subdomain: web-application-testing
tags: [directory-enumeration, ffuf, gobuster, web-recon, beginner, content-discovery]
difficulty: beginner
mitre_techniques: [T1595.003]
nist_csf_functions: [Identify]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/web-application/sqli-basics
---

> ⚠️ **Educational Use Only** — Directory brute-forcing against systems you don't own generates large numbers of requests and may be considered unauthorized access or a denial of service. Only perform this against systems you own, have written authorization to test, or dedicated lab environments.

## When to Use

- During the information gathering phase of an authorized web application pentest
- In CTF challenges where a hidden path, admin panel, or backup file contains the flag
- When performing authorized reconnaissance to map an application's full attack surface
- As a prerequisite for finding hidden admin panels, API endpoints, backup files (`config.php.bak`, `.git/`), and developer artifacts
- When validating that a WAF or server configuration correctly denies access to sensitive paths

## Prerequisites

- **Software:** Docker + Docker Compose (ffuf, gobuster, dirb pre-installed in lab)
- **Knowledge:** Basic understanding of HTTP status codes (200 OK, 301 Redirect, 403 Forbidden, 404 Not Found)
- **Lab:** `labs/web-application/sqli-basics` (shares environment)
- **Difficulty:** Beginner
- **Time:** 20–30 minutes

## Workflow

### Step 1: Start the Lab

```bash
agentlab start sqli-basics
agentlab exec sqli-basics bash
# Target: http://target:80
```

### Step 2: Basic Directory Fuzzing with ffuf

```bash
# Fast directory discovery
ffuf -u http://target:80/FUZZ \
     -w /usr/share/wordlists/dirb/common.txt \
     -mc 200,301,302,403

# With file extensions
ffuf -u http://target:80/FUZZ \
     -w /usr/share/wordlists/dirb/common.txt \
     -e .php,.html,.txt,.bak,.old \
     -mc 200,301,302,403
```

### Step 3: Recursive Enumeration

```bash
# Recursively fuzz found directories
ffuf -u http://target:80/FUZZ \
     -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
     -recursion -recursion-depth 2 \
     -mc 200,301,302
```

### Step 4: Filter Noise

```bash
# Filter by response size to remove false positives
ffuf -u http://target:80/FUZZ \
     -w /usr/share/wordlists/dirb/common.txt \
     -mc 200,301 \
     -fs 1234    # Filter responses of this exact size (false positives)

# Filter by word count
ffuf -u http://target:80/FUZZ \
     -w /usr/share/wordlists/dirb/common.txt \
     -fw 10      # Filter responses with exactly 10 words
```

### Step 5: Virtual Host Discovery

```bash
# Discover subdomains/vhosts by fuzzing the Host header
ffuf -u http://target:80/ \
     -H "Host: FUZZ.target" \
     -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
     -mc 200 \
     -fs 0    # Filter empty responses
```

### Step 6: Common High-Value Targets

Always check these manually after directory fuzzing:

```bash
for path in ".git" ".env" "admin" "backup" "config" "api" "swagger" "robots.txt" ".htaccess" "wp-login.php" "phpinfo.php" "server-status"; do
  code=$(curl -o /dev/null -s -w "%{http_code}" "http://target:80/$path")
  echo "$code $path"
done
```

### Step 7: Capture the Flag

A hidden admin directory contains the flag:

```bash
ffuf -u http://target:80/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200
# Finds: /admin-secret (200 OK)
curl http://target:80/admin-secret/
# FLAG{hidden_directory_found}
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| Fuzzing | Automated testing by trying many inputs from a wordlist |
| Wordlist | File of paths/names to test against (rockyou, SecLists, dirb/common.txt) |
| Status Code 403 | Forbidden — directory exists but access is denied (still valuable to document) |
| Content Discovery | Finding undocumented or unlinked parts of a web application |
| T1595.003 | MITRE ATT&CK: Active Scanning — Wordlist Scanning |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `ffuf` | Fast web fuzzer — highly configurable, best for filtering | ✅ Pre-installed |
| `gobuster` | Go-based directory/DNS/vhost brute forcer | ✅ Pre-installed |
| `dirb` | Classic directory brute forcer | ✅ Pre-installed |
| SecLists | Comprehensive wordlist collection | ✅ Pre-installed |

## Output / Verification

```bash
agentlab verify sqli-basics "FLAG{hidden_directory_found}"
```

## Further Reading

- [ffuf Documentation](https://github.com/ffuf/ffuf)
- [SecLists](https://github.com/danielmiessler/SecLists)
- MITRE ATT&CK: [T1595.003](https://attack.mitre.org/techniques/T1595/003/)
- [OWASP Testing: Enumerate Application on Webserver](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/04-Enumerate_Applications_on_Webserver)
