---
name: cracking-weak-hashes-in-lab-environment
description: >-
  Identify and crack weak password hashes (MD5, SHA1, NTLM, bcrypt) using
  dictionary attacks, rainbow tables, and rule-based mutations with Hashcat and
  John the Ripper inside an isolated lab environment. Covers hash identification,
  wordlist selection, and password policy auditing for security assessments.
domain: cybersecurity
subdomain: cryptography
tags: [hashcat, john-the-ripper, password-cracking, hashes, beginner, credential-access]
difficulty: beginner
mitre_techniques: [T1110.002]
nist_csf_functions: [Identify, Protect]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/cryptography/hash-cracking-lab
---

> ⚠️ **Educational Use Only** — Password hash cracking must only be performed on hashes you are authorized to test (hashes from systems you own, authorized penetration test targets, or purpose-built lab environments). Cracking credentials without authorization is illegal. These skills teach defenders to recognize weak password policies and improve them.

## When to Use

- After obtaining a password hash file from an authorized penetration test target (e.g., `/etc/shadow` dump, database credential leak)
- During CTF challenges where a hash is provided as part of the challenge
- When auditing an organization's password policy strength by cracking a sanitized sample of their hashed passwords
- When learning the difference between weak hashing algorithms (MD5, SHA1) and strong ones (bcrypt, Argon2)
- As a prerequisite for understanding credential stuffing, pass-the-hash, and authentication bypass techniques

## Prerequisites

- **Software:** Docker + Docker Compose (Hashcat + John pre-installed)
- **Knowledge:** What a hash function is, why passwords should be hashed and not stored in plaintext
- **Lab:** `labs/cryptography/hash-cracking-lab` — start with `agentlab start hash-cracking-lab`
- **Difficulty:** Beginner — no cryptography background required
- **Time:** 25–40 minutes

## Workflow

### Step 1: Start the Lab

```bash
agentlab start hash-cracking-lab
agentlab exec hash-cracking-lab bash
# A file /lab/hashes.txt is pre-populated with the challenge hashes
cat /lab/hashes.txt
```

### Step 2: Identify Hash Types

Before cracking, identify the hash algorithm:

```bash
# Use hash-identifier
hash-identifier

# Or use hashid
hashid /lab/hashes.txt

# Or recognize by length/format:
# MD5:    32 hex chars   e.g., 5f4dcc3b5aa765d61d8327deb882cf99
# SHA1:   40 hex chars   e.g., 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8
# SHA256: 64 hex chars
# NTLM:   32 hex chars   (same length as MD5, different structure)
# bcrypt: starts with $2a$ or $2b$
```

### Step 3: Dictionary Attack with Hashcat

The most effective cracking technique for common passwords:

```bash
# MD5 dictionary attack (mode 0)
hashcat -m 0 /lab/hashes.txt /usr/share/wordlists/rockyou.txt

# SHA1 dictionary attack (mode 100)
hashcat -m 100 /lab/hashes.txt /usr/share/wordlists/rockyou.txt

# NTLM dictionary attack (mode 1000)
hashcat -m 1000 /lab/hashes.txt /usr/share/wordlists/rockyou.txt

# bcrypt dictionary attack (mode 3200) — much slower
hashcat -m 3200 /lab/hashes.txt /usr/share/wordlists/rockyou.txt

# Show cracked hashes
hashcat -m 0 /lab/hashes.txt --show
```

### Step 4: Rule-Based Attack

Wordlist + mutation rules dramatically expand coverage:

```bash
# Apply best64 rules to rockyou (adds common mutations: password1, Password!, etc.)
hashcat -m 0 /lab/hashes.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule

# OneRuleToRuleThemAll (more comprehensive)
hashcat -m 0 /lab/hashes.txt /usr/share/wordlists/rockyou.txt -r /lab/OneRuleToRuleThemAll.rule
```

### Step 5: John the Ripper

John the Ripper auto-detects hash types and has built-in wordlists:

```bash
# Auto-detect and crack
john /lab/hashes.txt

# Use specific wordlist
john --wordlist=/usr/share/wordlists/rockyou.txt /lab/hashes.txt

# Show cracked
john --show /lab/hashes.txt

# Crack /etc/shadow format (lab provides a sample)
john --wordlist=/usr/share/wordlists/rockyou.txt /lab/shadow.txt
```

### Step 6: Crack the Salted Hash

The lab includes a salted MD5 hash. Identify the format:

```
$apr1$xyz$<hash>  — Apache MD5
$1$xyz$<hash>     — Linux MD5 crypt
```

```bash
# Hashcat mode for md5crypt (linux shadow)
hashcat -m 500 /lab/shadow_hash.txt /usr/share/wordlists/rockyou.txt
```

### Step 7: Capture the Flag

The flag is the plaintext password of the `admin` hash in `/lab/hashes.txt`:

```bash
hashcat -m 0 /lab/hashes.txt /usr/share/wordlists/rockyou.txt --show
# Output: 5f4dcc3b5aa765d61d8327deb882cf99:password
```

Submit: `agentlab verify hash-cracking-lab "password"`

## Key Concepts

| Concept | Definition |
|---------|-----------|
| Hash Function | One-way mathematical function that converts input to a fixed-size digest — cannot be reversed |
| Salt | Random value prepended/appended before hashing to prevent rainbow table attacks |
| Dictionary Attack | Hashing words from a wordlist and comparing against the target hash |
| Rule-Based Attack | Applying mutation rules (append numbers, capitalize, etc.) to wordlist entries |
| Brute Force | Systematically trying all possible character combinations — effective only for short passwords |
| Rainbow Table | Pre-computed hash→plaintext table — defeated by salts |
| bcrypt / Argon2 | Modern, intentionally slow hashing algorithms designed to resist cracking |
| T1110.002 | MITRE ATT&CK: Password Cracking |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `hashcat` | GPU-accelerated hash cracking | ✅ Pre-installed (CPU mode in lab) |
| `john` | CPU-based cracking with auto hash detection | ✅ Pre-installed |
| `hash-identifier` | Identifies hash algorithm from format/length | ✅ Pre-installed |
| `hashid` | Python-based hash type identifier | ✅ Pre-installed |
| RockYou.txt | 14M real-world leaked passwords wordlist | ✅ Pre-installed at `/usr/share/wordlists/` |

## Common Scenarios

### Scenario 1: Database Dump with MD5 Passwords

```bash
# hashes.txt content from a simulated DB dump:
# admin:5f4dcc3b5aa765d61d8327deb882cf99
# user1:d8578edf8458ce06fbc5bb76a58c5ca4

hashcat -m 0 hashes.txt rockyou.txt --username
# Cracks: admin:password, user1:qwerty
```

**Takeaway:** 80%+ of common passwords crack within minutes against MD5. MD5 must never be used for passwords.

### Scenario 2: Auditing Password Policy Strength

Given a sanitized sample of bcrypt hashes from an authorization holder:

```bash
hashcat -m 3200 sample_hashes.txt rockyou.txt -r best64.rule
```

If any crack within 24 hours, the organization's password policy is too weak.

### Scenario 3: NTLM Hashes from Windows Environment

```bash
# Format: username:RID:LMhash:NThash:::
# Example: Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::

hashcat -m 1000 nt_hashes.txt rockyou.txt
```

## Output / Verification

```bash
agentlab verify hash-cracking-lab "<plaintext-password>"
```

**Score:** 100 points per cracked hash (5 hashes total in lab)

## Further Reading

- [Hashcat Wiki](https://hashcat.net/wiki/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- MITRE ATT&CK: [T1110.002 — Password Cracking](https://attack.mitre.org/techniques/T1110/002/)
- [GTFOBins Hash Cracking Reference](https://gtfobins.github.io/)
