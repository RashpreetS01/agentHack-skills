# AgentHack-Skills

<p align="center">
  <img src="assets/banner.png" alt="AgentHack-Skills Banner" width="800"/>
</p>

<p align="center">
  <a href="https://github.com/mukul975/agentHack-skills/stargazers"><img src="https://img.shields.io/github/stars/mukul975/agentHack-skills?style=flat-square&color=gold" alt="Stars"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square" alt="License"/></a>
  <a href="https://github.com/mukul975/agentHack-skills/actions"><img src="https://img.shields.io/github/actions/workflow/status/mukul975/agentHack-skills/validate-skills.yml?label=skills%20valid&style=flat-square" alt="CI"/></a>
  <a href="index.json"><img src="https://img.shields.io/badge/skills-15-brightgreen?style=flat-square" alt="Skills"/></a>
  <img src="https://img.shields.io/badge/MITRE%20ATT%26CK-mapped-red?style=flat-square" alt="MITRE"/>
  <img src="https://img.shields.io/badge/Built%20with-Claude%20Code-orange?style=flat-square" alt="Built with Claude Code"/>
</p>

<p align="center">
  <strong>Ethical hacking skills + isolated Docker labs for AI agents, students, and security professionals.</strong><br/>
  100% safe. 100% educational. Built on the <a href="https://agentskills.io">agentskills.io</a> open standard.
</p>

---

> **⚠️ EDUCATIONAL USE ONLY**
> All skills and lab environments in this repository are designed exclusively for **legal, authorized, educational use** in **isolated, controlled environments**. Never use these techniques on systems you do not own or have explicit written permission to test. Use of these materials against unauthorized systems is illegal and unethical. The maintainers assume no liability for misuse. By using this repository, you agree to comply with all applicable laws.

---

## What Is This?

**AgentHack-Skills** is a companion repository to [Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) that adds:

| Feature | Description |
|---------|-------------|
| **15+ Ethical Hacking Skills** | agentskills.io YAML + Markdown format, MITRE ATT&CK mapped |
| **Docker Lab Environments** | Isolated, self-destructing vulnerable containers for every skill category |
| **MCP Server** | `agentlab` — lets Claude and any MCP-compatible agent spin up labs, execute commands, verify flags, and track progress |
| **Skill Progression** | Beginner → Intermediate → Advanced tracks with automated scoring |
| **Zero Real Risk** | All labs run on isolated Docker networks with no internet access. Containers auto-destruct after sessions. |

This project fills the gap that no other tool fills: **MIT-licensed, self-hostable, MCP-native, agentskills.io-formatted ethical hacking curriculum** that AI agents can drive autonomously.

---

## Quick Start

### Option A: Skills Only (No Docker Needed)

```bash
# Install via npx (agentskills.io standard)
npx skills add mukul975/agentHack-skills

# Or clone directly
git clone https://github.com/mukul975/agentHack-skills.git
```

Skills are immediately available to Claude Code, Cursor, GitHub Copilot, LangChain, and any agentskills.io-compatible agent.

### Option B: Full Lab Environment (Docker Required)

```bash
# 1. Clone the repo
git clone https://github.com/mukul975/agentHack-skills.git
cd agentHack-skills

# 2. Install the MCP server
cd mcp-server
pip install -e .

# 3. Start your first lab (SQL injection basics)
agentlab start sqli-basics

# 4. Or let Claude drive it entirely via MCP
# Add to your Claude Code config:
# { "mcpServers": { "agentlab": { "command": "agentlab", "args": ["serve"] } } }
```

That's it. One command. Claude can now autonomously practice ethical hacking in an isolated sandbox.

---

## Skills Index

All skills follow the [agentskills.io](https://agentskills.io) standard — YAML frontmatter + structured Markdown. MITRE ATT&CK and NIST CSF mapped throughout.

### Web Application Testing
| Skill | Difficulty | MITRE Technique |
|-------|-----------|-----------------|
| [Detecting SQL Injection Vulnerabilities](skills/detecting-sql-injection-vulnerabilities/SKILL.md) | Beginner | T1190 |
| [Detecting XSS Vulnerabilities in Web Apps](skills/detecting-xss-vulnerabilities-in-web-apps/SKILL.md) | Beginner | T1190 |
| [Detecting LFI / Path Traversal Vulnerabilities](skills/detecting-lfi-path-traversal-vulnerabilities/SKILL.md) | Intermediate | T1190 |
| [Analyzing JWT Token Security](skills/analyzing-jwt-token-security/SKILL.md) | Intermediate | T1552.001 |
| [Detecting SSRF Vulnerabilities](skills/detecting-ssrf-vulnerabilities/SKILL.md) | Intermediate | T1190 |
| [Detecting Insecure Deserialization Vulnerabilities](skills/detecting-insecure-deserialization-vulnerabilities/SKILL.md) | Advanced | T1190 |
| [Analyzing Web Application HTTP Headers](skills/analyzing-web-application-http-headers/SKILL.md) | Beginner | T1190 |
| [Performing Web Directory Enumeration](skills/performing-web-directory-enumeration/SKILL.md) | Beginner | T1595.003 |

### Network Reconnaissance
| Skill | Difficulty | MITRE Technique |
|-------|-----------|-----------------|
| [Performing Port Scanning in Safe Lab](skills/performing-port-scanning-in-safe-lab/SKILL.md) | Beginner | T1046 |
| [Analyzing Network Packet Captures](skills/analyzing-network-packet-captures/SKILL.md) | Intermediate | T1040 |

### Privilege Escalation
| Skill | Difficulty | MITRE Technique |
|-------|-----------|-----------------|
| [Detecting SUID Misconfigurations for PrivEsc](skills/detecting-suid-misconfigurations-for-privesc/SKILL.md) | Intermediate | T1548.001 |
| [Analyzing Sudo Rules for PrivEsc Vectors](skills/analyzing-sudo-rules-for-privesc-vectors/SKILL.md) | Intermediate | T1548.003 |

### Credential Security
| Skill | Difficulty | MITRE Technique |
|-------|-----------|-----------------|
| [Cracking Weak Hashes in Lab Environment](skills/cracking-weak-hashes-in-lab-environment/SKILL.md) | Beginner | T1110.002 |
| [Performing Password Spray in Lab](skills/performing-password-spray-in-lab/SKILL.md) | Intermediate | T1110.003 |

### Reconnaissance & OSINT
| Skill | Difficulty | MITRE Technique |
|-------|-----------|-----------------|
| [Performing OSINT Recon on Simulated Target](skills/performing-osint-recon-on-simulated-target/SKILL.md) | Beginner | T1589 |

---

## MCP Server — `agentlab`

The `agentlab` MCP server is the bridge between AI agents and safe lab environments.

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `list_challenges` | List all available lab challenges with difficulty and category |
| `get_challenge` | Get full details, hints, and learning objectives for a challenge |
| `start_lab` | Spin up an isolated Docker lab environment |
| `execute_in_lab` | Run a command inside the lab (sandboxed, no host access) |
| `verify_flag` | Submit a captured flag for verification |
| `get_progress` | Get current skill progression and completed challenges |
| `get_hint` | Get a progressive hint for the current challenge |
| `stop_lab` | Tear down the lab environment (auto-called on timeout) |

### Claude Code Integration

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "agentlab": {
      "command": "agentlab",
      "args": ["serve"],
      "env": {}
    }
  }
}
```

Then in Claude Code:

```
Use agentlab to start the sqli-basics challenge and solve it step by step, 
explaining each technique as you go.
```

---

## Integration with Anthropic-Cybersecurity-Skills

This repo is a direct companion to [Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) (4k+ stars).

- **Same format**: identical agentskills.io YAML frontmatter + Markdown structure
- **Complementary domains**: the parent repo covers defensive/analysis skills; this repo covers offensive/practice skills in safe lab environments
- **Shared index**: both repos are discoverable via `npx skills search cybersecurity`
- **Combined MITRE coverage**: together they cover all 14 Enterprise ATT&CK tactics

Install both:
```bash
npx skills add mukul975/Anthropic-Cybersecurity-Skills
npx skills add mukul975/agentHack-skills
```

---

## Lab Architecture (Safety Design)

Every lab environment is engineered to be **safe by construction**:

```
┌─────────────────────────────────────────────────────┐
│                  Docker Isolated Network              │
│                  (no internet, no host)               │
│                                                       │
│   ┌─────────────┐         ┌─────────────────────┐   │
│   │  Attacker   │◄───────►│   Target (Vulnerable │   │
│   │  Container  │         │   App / Service)     │   │
│   │  (tools)    │         │                      │   │
│   └─────────────┘         └─────────────────────┘   │
│                                                       │
│   Auto-destructs after session timeout (default: 1h) │
└─────────────────────────────────────────────────────┘
```

Safety guarantees:
- **No internet access**: `internal: true` on all Docker networks
- **No host filesystem access**: no volume mounts to host paths
- **Auto-cleanup**: containers destroyed after timeout (configurable)
- **Flag-based verification**: completion is verified by capturing a flag string, not by actual exploitation
- **Synthetic targets only**: all vulnerable apps are purpose-built educational tools (WebGoat, DVWA, custom apps)

---

## Roadmap

- [x] v0.1.0 — 15 skills, 9 lab environments, MCP server
- [ ] v0.2.0 — 30 skills, Active Directory labs, agent trajectory export (CSAW format)
- [ ] v0.3.0 — Web dashboard, leaderboard, team mode for bootcamps
- [ ] v0.4.0 — Adaptive difficulty (tracks agent capability signals)
- [ ] v0.5.0 — CTF competition mode, automated challenge generation

---

## Contributing

We welcome new skills and lab environments. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

Quick checklist:
- [ ] Skill follows agentskills.io YAML + Markdown format (see [template](CONTRIBUTING.md#skill-template))
- [ ] Lab environment uses Docker Compose, isolated network, no internet
- [ ] Includes safety disclaimer in SKILL.md header
- [ ] MITRE ATT&CK technique(s) referenced in skill body
- [ ] Lab has a flag verification mechanism
- [ ] Apache 2.0 LICENSE file included

---

## License

[Apache 2.0](LICENSE) — free to use, fork, and build on. Attribution required.

---

## Citation

```bibtex
@software{agenthack_skills_2026,
  author = {mukul975},
  title = {AgentHack-Skills: Ethical Hacking Skills for AI Agents},
  year = {2026},
  url = {https://github.com/mukul975/agentHack-skills},
  license = {Apache-2.0}
}
```

---

<p align="center">Built with <a href="https://claude.ai/code">Claude Code</a> · Companion to <a href="https://github.com/mukul975/Anthropic-Cybersecurity-Skills">Anthropic-Cybersecurity-Skills</a></p>
