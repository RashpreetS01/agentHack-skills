# Contributing to AgentHack-Skills

Thank you for helping make ethical hacking education safer and more accessible.

> **Before contributing**, read the [Security Policy](SECURITY.md) and [Code of Conduct](CODE_OF_CONDUCT.md). All contributions must be safe, educational, and legal.

---

## Types of Contributions

| Type | Description |
|------|-------------|
| **New Skill** | A new agentskills.io-formatted skill with a companion lab environment |
| **New Lab** | A standalone Docker Compose vulnerable environment |
| **Skill Improvement** | Better instructions, clearer steps, additional MITRE mappings |
| **Bug Fix** | Fix in MCP server, lab configuration, or CI/CD |
| **Documentation** | Improve README, skill docs, or guides |

---

## Skill Template

Every skill must follow this exact structure:

### YAML Frontmatter (required)

```yaml
---
name: kebab-case-skill-name
description: >-
  One or two sentences (100-200 chars) describing what this skill does
  and when an AI agent or student should use it. Include key terms.
domain: cybersecurity
subdomain: web-application-testing
tags: [sqli, injection, owasp, web-security, beginner]
difficulty: beginner
mitre_techniques: [T1190]
nist_csf_functions: [Identify, Protect]
version: "1.0"
author: your-github-username
license: Apache-2.0
lab_environment: labs/web-application/sqli-basics
---
```

**Required fields:** `name`, `description`, `domain`, `subdomain`, `tags`, `difficulty`, `version`, `author`, `license`

**Optional but strongly encouraged:** `mitre_techniques`, `nist_csf_functions`, `lab_environment`

### Markdown Body (required sections, in order)

```markdown
> ⚠️ **Educational Use Only** — Practice this skill only in the provided lab 
> environment or other authorized sandboxes. Never use on unauthorized systems.

## When to Use

[3-5 bullet points describing situations where this skill applies]

## Prerequisites

- **Software:** [tools needed]
- **Knowledge:** [concepts to understand first]
- **Lab:** [link to companion lab environment]
- **Difficulty:** Beginner / Intermediate / Advanced

## Workflow

[Numbered steps with commands. All commands run inside the lab container.]

### Step 1: [Action]
...

## Key Concepts

| Concept | Definition |
|---------|-----------|
| ... | ... |

## Tools

| Tool | Purpose | Lab Availability |
|------|---------|-----------------|
| ... | ... | ✅ Pre-installed |

## Common Scenarios

[2-3 walkthrough examples using the lab environment]

## Output / Verification

[What success looks like — flag format, expected output, scoring]

## Further Reading

- [Link to relevant OWASP/CVE/NIST resource]
- MITRE ATT&CK: [T####](https://attack.mitre.org/techniques/T####/)
```

---

## Lab Environment Requirements

Every Docker Compose lab must:

1. **Use isolated networks** — `networks: lab_net: internal: true`
2. **Not mount host paths** — no `volumes` pointing outside `/opt/labs/`
3. **Include a `lab.json`** with metadata:
   ```json
   {
     "id": "sqli-basics",
     "name": "SQL Injection Basics",
     "difficulty": "beginner",
     "category": "web-application",
     "flags": [{ "id": "flag1", "hash": "sha256-of-flag-value", "points": 100 }],
     "timeout_minutes": 60,
     "learning_objectives": ["..."]
   }
   ```
4. **Include a `setup.sh`** that initializes the environment and plants flags
5. **Pass the safety checklist:**
   - [ ] No internet access from containers
   - [ ] No privileged containers (unless absolutely required and documented)
   - [ ] Flags are synthetic strings, not real credentials
   - [ ] README explains the learning objective clearly

---

## Pull Request Process

1. Fork the repo and create a feature branch: `git checkout -b skill/my-new-skill`
2. Add your skill following the template above
3. Validate locally: `python scripts/validate_skills.py`
4. Update `index.json`: `python scripts/generate_index.py`
5. Open a PR with the `skill-submission` template
6. A maintainer will review within 7 days

---

## Skill Subdomain Values

Use one of the following for `subdomain`:

- `web-application-testing`
- `network-reconnaissance`
- `privilege-escalation`
- `credential-access`
- `cryptography`
- `osint-reconnaissance`
- `forensics`
- `reverse-engineering`
- `cloud-security`
- `active-directory`
- `social-engineering-awareness`
- `mobile-security`

---

Questions? Open a [Discussion](https://github.com/mukul975/agentHack-skills/discussions).
