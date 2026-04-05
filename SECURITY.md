# Security Policy

## Ethical Use Statement

AgentHack-Skills is designed **exclusively for legal, authorized, educational use** in isolated, controlled environments.

**Do not use any skill or lab environment in this repository to:**
- Test, probe, or attack systems you do not own
- Test systems without explicit written authorization from the owner
- Conduct any activity that violates local, national, or international law
- Harm, disrupt, or degrade any production system or service

**By using this repository, you agree that:**
1. You will only practice in the provided Docker lab environments or other authorized sandboxes
2. You take full legal and ethical responsibility for any use of these materials
3. You will report any safety concerns about lab escape or unintended access to the maintainers immediately

## Reporting Vulnerabilities in This Repo

If you find a security issue **in the lab environments themselves** (e.g., a container escape, unintended network access beyond the isolated network, or a flag bypass that doesn't require completing the learning objectives), please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Email: security@[maintainer-domain] (or open a private security advisory on GitHub).

Include:
- Description of the issue
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and aim to release a fix within 7 days for critical issues.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes |
| < 0.1   | ❌ No |

## Safety Architecture

All lab environments are designed with defense-in-depth:
- Isolated Docker networks (`internal: true`) — no internet routing
- No host filesystem mounts
- Automatic container cleanup after session timeout
- Synthetic, purpose-built vulnerable targets only (no real CVEs against real software versions that could be exploited outside the lab)
- Flag-based verification (completion requires understanding, not just execution)
