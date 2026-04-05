# Launch Copy — AgentHack-Skills v0.1.0

Copy-paste ready launch content for X, Reddit, HN, and LinkedIn.

---

## X / Twitter Thread

**Tweet 1 (Hook):**
```
I built the missing piece in AI security education.

15 ethical hacking skills + isolated Docker labs, all in agentskills.io format so Claude can practice hacking SAFELY.

No internet access. No real systems. Just learning.

Companion to my 4k-star Anthropic-Cybersecurity-Skills repo.

Thread 🧵
```

**Tweet 2 (Problem):**
```
The problem:

- TryHackMe / HackTheBox = built for humans, terrible for AI agents
- No API, no programmatic flag submission, no skill format

AI agents like Claude literally can't "practice" hacking on any existing platform in a structured way.

Until now.
```

**Tweet 3 (Solution):**
```
AgentHack-Skills:

✅ 15 skills in YAML+Markdown (agentskills.io standard)
✅ Docker labs that self-destruct after sessions
✅ MCP server so Claude can spin up labs, exec commands, verify flags
✅ All isolated — no internet, no host access
✅ MITRE ATT&CK mapped
✅ MIT licensed

One command: npx skills add mukul975/agentHack-skills
```

**Tweet 4 (Demo):**
```
You can literally tell Claude:

"Use agentlab to start the SQL injection challenge, solve it step by step, and explain what you learn"

And it will:
→ spin up DVWA in Docker
→ enumerate injection points
→ extract the flag
→ auto-destruct the container when done

All in isolation. Zero real risk.
```

**Tweet 5 (Safety):**
```
Safety is non-negotiable here.

Every lab:
- internal: true Docker networks (no internet routing)
- no host filesystem mounts
- auto-cleanup after timeout
- synthetic targets only (no real CVEs against live software)

This is education, not hacking.
```

**Tweet 6 (Integration):**
```
It integrates directly with my other repo:

Anthropic-Cybersecurity-Skills (4k ⭐)
→ 754 defensive/analysis skills

AgentHack-Skills (new)
→ 15 offensive/practice skills in safe labs

Together: complete red+blue team curriculum for AI agents

npx skills add both and you have a full security training system
```

**Tweet 7 (CTA):**
```
GitHub: github.com/mukul975/agentHack-skills

⭐ Star if you want AI-native security education to be a thing
🍴 Fork to contribute labs and skills (CONTRIBUTING.md)
🔔 Watch for v0.2.0 — Active Directory labs coming

Built with Claude Code. Apache 2.0. 100% safe.
```

---

## Reddit Posts

### r/netsec

**Title:** AgentHack-Skills — Ethical hacking skills in agentskills.io format with isolated Docker labs and an MCP server for AI agents [Apache 2.0]

**Body:**
```
Hey r/netsec,

I just open-sourced AgentHack-Skills: https://github.com/mukul975/agentHack-skills

**What it is:**
15 ethical hacking skills in the agentskills.io YAML+Markdown format (same format as my Anthropic-Cybersecurity-Skills repo with 4k stars), each paired with an isolated Docker lab environment.

**The MCP server** (`agentlab`) lets Claude and other AI agents:
- Spin up Docker-based vulnerable environments
- Execute commands inside isolated containers
- Verify flag captures (CTF-style)
- Track skill progression
- Auto-destroy containers when done

**Safety by design:**
- All Docker networks use `internal: true` — no internet routing
- No host filesystem mounts
- Containers auto-cleanup after session timeout
- Only synthetic vulnerable targets (DVWA, purpose-built apps)

**Skills covered:**
- SQLi, XSS, LFI, SSRF, Deserialization, JWT security, HTTP headers
- Port scanning, packet capture analysis
- SUID and sudo privilege escalation
- Hash cracking, password spraying
- OSINT on simulated targets

**Why it's different from TryHackMe/HTB:**
Those platforms have no API. AI agents literally cannot interact with them programmatically. This is built from the ground up to be agent-native.

**License:** Apache 2.0

Would love feedback from this community — especially on lab design and additional skill ideas.
```

### r/hacking (learning/educational)

**Title:** I made a free, open-source ethical hacking lab environment for AI agents and students — Docker-based, self-destructing, MIT licensed

**Body:**
```
Built AgentHack-Skills as a companion to my existing Anthropic-Cybersecurity-Skills repo.

Core idea: every "ethical hacking skill" (SQLi, XSS, SUID privesc, etc.) is paired with a Docker Compose lab that:
1. Spins up in one command
2. Has zero internet access (isolated Docker network)
3. Contains a CTF-style flag to capture
4. Auto-destructs when the session ends

An MCP server lets Claude or any AI agent control the entire flow autonomously.

All instructions in the SKILL.md files are educational and defensive — the goal is always to understand the vulnerability so you can fix it.

Good for:
- Security bootcamp students
- CTF beginners
- AI agent developers building security tooling
- Defenders who want to understand attacker techniques

Free, Apache 2.0: https://github.com/mukul975/agentHack-skills
```

---

## Hacker News

**Title:** AgentHack-Skills: Ethical hacking skills in agentskills.io format with Docker labs and MCP server for AI agents

**Body:**
```
I'm the maintainer of Anthropic-Cybersecurity-Skills (754 defensive security skills, 4k GitHub stars). Today I'm releasing its companion: AgentHack-Skills.

The problem I'm solving: no existing ethical hacking platform (TryHackMe, HackTheBox, OverTheWire) exposes an API that allows AI agents to interact programmatically. They're all browser/GUI-first. The closest open alternative, Amazon's CTF-Dojo, has 40 stars and a CC-BY-NC license.

AgentHack-Skills is:
1. MIT-licensed and self-hostable (docker compose up)
2. Built around the agentskills.io standard — same YAML+Markdown format AI agents already know
3. Ships an MCP server (agentlab) so Claude and GPT can spin up labs, run commands in isolation, and verify flag captures
4. Engineered for safety: internal Docker networks only, no host mounts, auto-cleanup

v0.1.0 ships with 15 skills and 3 full Docker lab environments covering web app testing, network recon, and Linux privilege escalation.

GitHub: https://github.com/mukul975/agentHack-skills

The interesting design question I'd love feedback on: should AI agents that "solve" ethical hacking challenges generate structured trajectory logs (like CTF-Dojo does)? That data could be used to fine-tune better security-aware models.
```

---

## LinkedIn

```
Excited to release AgentHack-Skills — a new open-source project I've been building.

If you follow my work, you know I maintain Anthropic-Cybersecurity-Skills: 754 MITRE-mapped defensive security skills for AI agents (4k+ GitHub stars).

AgentHack-Skills is the companion: 15 ethical hacking skills in the same agentskills.io format, but for practice in completely isolated Docker lab environments.

The key innovation: an MCP server called `agentlab` that lets Claude (and any MCP-compatible agent) autonomously:
→ Spin up isolated vulnerable environments
→ Execute security commands in complete isolation
→ Verify flag captures
→ Track skill progression

Everything is safe by design:
- Internal Docker networks (zero internet routing)
- No host filesystem access
- Containers self-destruct after sessions
- Synthetic targets only

This is for students, bootcamp learners, security professionals, and AI developers building security tooling — not for malicious use.

Apache 2.0. One command to start: `npx skills add mukul975/agentHack-skills`

GitHub: https://github.com/mukul975/agentHack-skills

What ethical hacking challenge would you most want to practice with an AI agent? Drop it in the comments.

#cybersecurity #ethicalhacking #opensourcesecurity #AIagents #Claude #security
```

---

## Weekly Maintainer Plan

### Week 1 (Launch Week)
- [ ] Push v0.1.0 release tag
- [ ] Post all launch content above
- [ ] Respond to every GitHub issue and comment within 24h
- [ ] Post on security Discord servers (TryHackMe Discord, HTB Discord, OWASP chapters)

### Week 2-3
- [ ] Add 5 more skills (aim for 20 total)
- [ ] Add Active Directory lab (Bloodhound-style enumeration)
- [ ] Improve MCP server — add progress persistence via SQLite

### Week 4 (v0.2.0)
- [ ] Tag v0.2.0 with AD labs
- [ ] Post update thread on X
- [ ] Cross-post update to r/netsec

### Monthly
- [ ] Review open issues/PRs
- [ ] Add 3-5 community-contributed skills
- [ ] Update MITRE coverage map
- [ ] Check if any companion Anthropic-Cybersecurity-Skills updates need reflected here
- [ ] Run: `python scripts/generate_index.py && python scripts/validate_skills.py`
