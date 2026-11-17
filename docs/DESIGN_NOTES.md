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
- **Name:** Starling (the repository is still named strategy-mirror). The starling imagery is the visual metaphor as the visual metaphor: the North Star is the company vision; the flock is the people and teams; tightness reflects alignment.
- **Layout:** six tabbed views (Overview, Strategy, Work, Decisions, Open questions, Review), rebuilt from screenshots of the later design. The earlier single-page layout and its scripted chat were retired; the "Classic view" toggle from the later design was left out for now.
- **Skins:** one look (modern) on a shared base; more can be added. See `SKINS.md`.
- **Target:** desktop first. Phone width stacks and scrolls wide boards inside their own box.
- **Delivery:** bespoke per client. Prerequisites: somewhere to host code (GitHub by default) and a database (Sheets, Excel, Airtable or other, decided in onboarding). Everything stays on the client's internal infrastructure.

## Assumptions (not yet confirmed)
- Initiative-to-objective links are set during onboarding or edited in the tool; where they come from varies by client.
- Effort is measured in FTE per initiative, a rough proxy to be revisited.
- Effect-delay lengths and research/discovery windows in the mockup are invented sample values.

## Open items
- The mockup is a static page with generated placeholder data. Contributions, challenges, review approvals, decision choices and folder scans all need a backend and a storage layer; nothing is saved yet.
- The data store, issue tracker and other client terms come from the data file (`text` block); the real store is decided in onboarding.
- Ask Starling (chat overlay) is back as a side panel. The sample answers from page data; the live version needs a model inside the client's network and a decision on what it may read.
- Review actions (mark reviewed, challenge, prefer a value) work in the page only. The storage adapter must implement `STARLING_HOOKS.onReview`.
- Because the database varies by client, a storage adapter layer is likely needed. Not designed yet.
- Onboarding asks only technical questions, derives the rest from the client's material with a source and quote for each item, and asks the client to confirm or challenge it. The rewritten prompt and template (0.2.0) have not been run against a real client.
- No independent audit (Codex or other) has been run on the prompt, template or mockup.

- **Open (design):** the animation has only been checked in a headless browser, not on real screens. Tagline wording ("Enabling strategic alignment") is a placeholder; alternatives considered: "Fly the same way", "One flock, one star".

## Principle: a mirror, not an oracle

The page shows what the documents, work and data say, including where they disagree; it does not say what the strategy should be, and the first picture may be wrong. Everything imported is shown as a best guess. Anything conflicting, low confidence, single-source, stale or without an owner is flagged for review by the role that can resolve it, and anyone can challenge anything. The aim is a single source of truth over time. That depends on knowledgeable owners reviewing what is shown, which the tool cannot guarantee.

Open: how to show reviewed items differently from unreviewed ones without marking everything on day one.

## Accessibility (current state)

- Done: focus stays on the control you used when a view redraws; the drawer is a modal dialog (focus moves in, is trapped, returns to the opener, and the page behind it is inert); view changes are announced; roadmap bars and target diamonds have text labels; the flock has a Pause motion button and stays still when the system asks for reduced motion.
- Board boxes are focusable groups with a text label and `aria-current` when selected. Tracing a box with the keyboard works (Enter or Space), but a screen-reader-first alternative to the wires, such as a list of linked items in the drawer, is still to do.
- Not yet checked with a real screen reader or in a browser's accessibility tools; testing so far used a scripted DOM only.

## Data checks roll up

When more than 5 items fail the same data check (currently: initiative with no FTE), the Review tab shows one row ("N initiatives have no FTE...") with a list. Five or fewer stay as single rows. Threshold: `DC_ROLLUP` in `design/src/base.html`.
