# Design notes

Decisions and open items from the initial design session. Update as implementations teach us more.

## Purpose
Show, for one company, division or team: what the strategy documents say (said), what work and data show (done), and what people understand (understood). Surface gaps and open questions. It does not make decisions.

## Decisions so far
- **Organising principle:** Martin Eriksson's Decision Stack. Source checked: Mind the Product article (Jan 2021) names Clear Vision, Structured Principles, Good Strategy, and Objectives and Impact. The article's diagram, which would confirm the order, could not be read. An extra division/product-line tier (4a) sits under Objectives where needed.
- **Strategy structure:** baseline (current state), aspiration (target), hypothesis (intermediate steps), each with narrative and metrics, plus milestones and decision points. Decision points can also be triggered by market or assumption changes and by signals in data.
- **Roadmap view:** follows Itamar Gilad's outcome roadmap template: goal bars with a target diamond, then Research, Product Discovery, Product Delivery (ideas inside a dashed box, or "to be determined"), and Effect Delay. Source: itamargilad.com/outcome-roadmaps. A by-team view is an addition not in Gilad's template.
- **Confidence:** each item carries a validated / partly validated / hypothesis marker.
- **Alignment:** every initiative links to zero or more objectives. Work linked to none is shown as unaligned.
- **Name:** Starling. The North Star is the company vision; the flock is the people and teams; tightness reflects alignment.
- **Skins:** two looks (starling, modern) share one base. See `SKINS.md`.
- **Target:** desktop only for now. No phone layout.
- **Delivery:** bespoke per client. Prerequisites: somewhere to host code (GitHub by default) and a database (Sheets, Excel, Airtable or other, decided in onboarding). Everything stays on the client's internal infrastructure.

## Assumptions (not yet confirmed)
- Initiative-to-objective links are set during onboarding or edited in the tool; where they come from varies by client.
- Effort is measured in FTE per initiative, a rough proxy to be revisited.
- Effect-delay lengths and research/discovery windows in the mockup are invented sample values.

## Open items
- The mockup is a static page. Writing answers back, the approval queue, folder scans and the chat all need a backend and a storage layer; not designed yet.
- Because the database varies by client, a storage adapter layer is likely needed. Not designed yet.
- Onboarding prompt and profile template have not been run against a real client.
- No independent audit (Codex or other) has been run on the prompt, template or mockup.

- **Open (design):** the animation has only been checked in a headless browser, not on real screens. Tagline wording ("Enabling strategic alignment") is a placeholder; alternatives considered: "Fly the same way", "One flock, one star".
