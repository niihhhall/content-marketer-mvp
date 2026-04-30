# Deep Research command

Use this command to launch a deep, multi-agent research session on any topic.

## Usage
`/deep-research "Your research topic or brain dump"`

## Flow
1. **Scope Interview**: Claude will ask 3-4 questions to narrow the focus.
2. **Recon**: A shallow sweep to identify key platforms and queries.
3. **Parallel Topic Agents**: Deep dives into specific angles of the topic.
4. **Critic**: Review and challenge claims.
5. **Synthesis**: Final consolidated report.

The output will be saved in `outputs/deep-research/{date}-{topic}/`.
Refer to `.claude/skills/deep-research/SKILL.md` for full logic.
