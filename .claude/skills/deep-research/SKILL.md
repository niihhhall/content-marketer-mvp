---
name: deep-research
description: >
  Multi-platform research using parallel AI agents. Use when: deep research,
  investigate a topic, find signal, intelligence gathering, who are the thought
  leaders on X, what's happening in Y.
user-invocable: true
effort: high
---

# Deep Research Protocol

Follow this multi-stage workflow to execute a high-fidelity research project.

## Phase 1: Scope Interview
- Ask the user 3-4 targeted questions to clarify:
  1. The specific goal (What decision are you trying to make?).
  2. Known constraints or assumptions.
  3. Desired depth (High-level summary vs. Raw data).
  4. Preferred platforms (e.g., skip X, focus on Reddit).

## Phase 2: Recon Agent (Sonnet)
- Load `prompts/recon.md`.
- Use `firecrawl`, `google_search`, or `x-search` to find where the signal lives.
- Output: A list of 3-6 specific angles, key search queries, and people to track.
- **Human Checkpoint**: Present the research plan to the user for approval.

## Phase 3: Parallel Topic Agents (Opus)
- Load `prompts/topic-agent.md`.
- **CRITICAL**: Launch all topic agents in a SINGLE message using multiple `Agent` tool calls.
- Each agent must write its output to a specific file: `outputs/deep-research/{session}/0x-{angle}.md`.
- Enforce the **Signal Quality Rubric**:
  - Score sources (Recency, Specificity, Primary vs. Aggregator).
  - Triangulate claims across at least 3 sources.

## Phase 4: Critic Agent (Opus)
- Load `prompts/critic.md`.
- Read all topic reports.
- Challenge weak claims, logical gaps, and unsupported assertions.
- Output: `outputs/deep-research/{session}/critic-notes.md`.

## Phase 5: Synthesis Agent (Opus)
- Load `prompts/synthesis.md`.
- Read topic reports and critic notes.
- Produce the final consolidated report at `outputs/deep-research/{session}/synthesis.md`.

## Output Structure
Use `{YYYY-MM-DD}-{topic-name}` for the session folder.
Every stage must log its raw output to the session folder.
