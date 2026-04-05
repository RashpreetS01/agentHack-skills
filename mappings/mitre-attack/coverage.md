# MITRE ATT&CK Coverage

AgentHack-Skills v0.1.0 — 15 skills covering 14 unique ATT&CK techniques across 6 tactics.

## Coverage Summary

| Tactic | Techniques Covered | Skills |
|--------|-------------------|--------|
| Initial Access | T1190 (Exploit Public-Facing Application) | SQLi, XSS, LFI, SSRF, Deserialization, HTTP Headers, Password Spray |
| Reconnaissance | T1589, T1590, T1591, T1595.001, T1595.003, T1596 | OSINT, Port Scanning, Dir Enumeration |
| Discovery | T1046, T1083 | Port Scanning, LFI |
| Credential Access | T1040, T1110.002, T1110.003, T1552.001, T1557 | Packet Capture, Hash Cracking, Password Spray, JWT |
| Privilege Escalation | T1548.001, T1548.003 | SUID PrivEsc, Sudo PrivEsc |
| Execution | T1059, T1059.007 | Deserialization RCE, XSS JS Execution |

## Technique Index

| Technique | ID | Skills |
|-----------|-----|--------|
| Exploit Public-Facing Application | T1190 | detecting-sql-injection-vulnerabilities, detecting-xss-vulnerabilities-in-web-apps, detecting-lfi-path-traversal-vulnerabilities, detecting-ssrf-vulnerabilities, detecting-insecure-deserialization-vulnerabilities, analyzing-web-application-http-headers |
| Network Sniffing | T1040 | analyzing-network-packet-captures |
| Network Service Discovery | T1046 | performing-port-scanning-in-safe-lab |
| File and Directory Discovery | T1083 | detecting-lfi-path-traversal-vulnerabilities |
| Password Cracking | T1110.002 | cracking-weak-hashes-in-lab-environment |
| Password Spraying | T1110.003 | performing-password-spray-in-lab |
| Credentials from Files | T1552.001 | analyzing-jwt-token-security |
| Valid Accounts | T1078 | analyzing-jwt-token-security |
| Adversary-in-the-Middle | T1557 | analyzing-network-packet-captures |
| Command and Scripting Interpreter | T1059 | detecting-insecure-deserialization-vulnerabilities |
| JavaScript | T1059.007 | detecting-xss-vulnerabilities-in-web-apps |
| Setuid and Setgid | T1548.001 | detecting-suid-misconfigurations-for-privesc |
| Sudo and Sudo Caching | T1548.003 | analyzing-sudo-rules-for-privesc-vectors |
| Gather Victim Identity Information | T1589 | performing-osint-recon-on-simulated-target |
| Gather Victim Network Information | T1590, T1590.004 | performing-osint-recon-on-simulated-target, detecting-ssrf-vulnerabilities |
| Active Scanning — IP Scanning | T1595.001 | performing-port-scanning-in-safe-lab |
| Active Scanning — Wordlist Scanning | T1595.003 | performing-web-directory-enumeration |
| Search Open Technical Databases | T1596 | performing-osint-recon-on-simulated-target |
| Gather Victim Host Information — Software | T1592.002 | analyzing-web-application-http-headers |

## Combined Coverage with Anthropic-Cybersecurity-Skills

When used alongside [Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills), total ATT&CK coverage spans all 14 Enterprise tactics with 290+ techniques covered.

- **This repo:** Offensive/practice skills (red team perspective, safe lab environments)
- **Parent repo:** Defensive/analysis skills (blue team perspective, DFIR, threat intelligence)

Together they provide a complete offense ↔ defense learning curriculum for AI agents and security practitioners.
