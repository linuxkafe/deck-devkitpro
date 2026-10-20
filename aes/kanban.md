---
project: deck-devkitpro
created: 2026-10-20
current_sprint: sprint-04
current_ticket: ""
---

# deck-devkitpro — Kanban

## Project Goal
Install devkitpro inside a podman container running on the Steam Deck
(`deck@steamdeck`), reachable via SSH, and expose a **MCP server** that this
OpenCode session consumes for Nintendo 3DS compilation. The service runs on
the Deck and delivers tooling here over MCP.

## Sprints

| Sprint | Goal | Status |
|--------|------|--------|
| sprint-01 | Project scaffolding + reconnaissance + kanban | done |
| sprint-02 | devkitpro install + MCP server + OpenCode wiring + e2e compile | done |
| sprint-03 | Decky plugin for on/off control on Steam Deck | done |
| sprint-04 | README + GitHub init + release | done |

## Tickets

| ID | Title | Sprint | Priority | Status |
|----|-------|--------|----------|--------|
| T001 | Scaffold AES project structure | sprint-01 | high | done |
| T002 | Install devkitpro in podman container on Deck | sprint-02 | high | done |
| T003 | Implement MCP server exposing 3DS compile tooling | sprint-02 | high | done |
| T004 | Wire MCP into OpenCode config | sprint-02 | medium | done |
| T005 | End-to-end 3DS hello-world compile test | sprint-02 | high | done |
| T006 | Decky plugin — on/off control + status UI | sprint-03 | high | done |
| T007 | README.md + GitHub repo init + release | sprint-04 | medium | done |