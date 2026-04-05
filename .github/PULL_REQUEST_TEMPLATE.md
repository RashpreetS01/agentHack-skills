## Pull Request

**Type:** <!-- New Skill / New Lab / Skill Improvement / Bug Fix / Documentation -->

**Skill(s) affected:**
<!-- e.g., detecting-sql-injection-vulnerabilities -->

---

## Description
<!-- What does this PR add or change? -->

## Safety Checklist (REQUIRED for all skill/lab changes)

- [ ] Skill includes the `⚠️ Educational Use Only` disclaimer in the header
- [ ] All lab containers use `internal: true` Docker networks (no internet access)
- [ ] No host path mounts (`volumes` only reference internal paths)
- [ ] Flags are synthetic strings, not real credentials or PII
- [ ] MITRE ATT&CK technique(s) referenced in SKILL.md body
- [ ] Apache 2.0 `LICENSE` file present in skill directory

## Skill Format Checklist

- [ ] YAML frontmatter has all required fields (`name`, `description`, `domain`, `subdomain`, `tags`, `difficulty`, `version`, `author`, `license`)
- [ ] Markdown sections in correct order: When to Use → Prerequisites → Workflow → Key Concepts → Tools → Output / Verification → Further Reading
- [ ] Commands in code blocks use correct tool names
- [ ] index.json regenerated: `python scripts/generate_index.py`

## Testing

<!-- How did you test this? -->
- [ ] Ran `python scripts/validate_skills.py` — passed
- [ ] Ran `docker compose up` for the lab — containers started successfully
- [ ] Verified flag capture works: `agentlab verify <lab-id> <flag>`

## Related Issues
<!-- Closes #XXX -->
