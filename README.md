# Strategy Mirror (working name)

A private, per-client tool that shows what a company's strategy documents say, what its work and data show, and what people understand the strategy to be, organised on Martin Eriksson's Decision Stack, with gaps, owners, open questions and a chat interface over the accumulated knowledge.

It does not make decisions. It supports better discussion and faster decisions.

## Status

Early. Each implementation is built bespoke for a client. Only the onboarding step is defined so far.

## Contents

| Path | Purpose |
| --- | --- |
| `onboarding/ONBOARDING_PROMPT.md` | Prompt the client's Claude runs as a guided interview |
| `onboarding/profile.template.yaml` | Blank, versioned profile the interview fills in |
| `design/mockup.html` | Static desktop mockup on a fictional company (open in a browser) |
| `docs/DESIGN_NOTES.md` | Design decisions, assumptions and open items |

## Prerequisites per client

- A place to host the code (GitHub by default).
- A database the client can use (for example Google Sheets, Excel on SharePoint, Airtable, or a SQL database). Onboarding finds out what is available and what it can and cannot do.

## Using it

1. Create a private repo for the client and copy this package into it.
2. Run the onboarding prompt. It writes `client/onboarding/profile.yaml` and `client/onboarding/readiness-report.md`.
3. Everything specific to the client stays under `client/`. The generic repo's `.gitignore` excludes `client/` so nothing client-specific is committed by accident; in the client's own private repo, remove that line.

## Rules

- The generic files must contain nothing that identifies a client.
- Unknown values stay `null`; assumptions are labelled and have an owner to check them.
