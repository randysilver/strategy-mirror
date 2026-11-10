# Skins

The page is built from one shared base plus a small skin per look, so a client can pick a style (or have one made) without touching the logic.

```
design/
  src/base.html          shared page: content, structure, data, scripts, default hero layout
  skins/<name>/
    tokens.css           colour and font tokens (light and dark, or one look)
    skin.css             overrides for shape, type and the hero
    config.json          page title, hero wording, and flock style
    fonts.txt            Google Fonts stylesheet URL
  build.py               builds each skin into design/dist/<name>.html
```

Build: `python design/build.py`. For hosts that add their own page skeleton: `python design/build.py --bare <dir>`.

## The shared idea (all skins)

- **North Star:** the company vision.
- **Flock:** each bird is a team or person. Tightness is computed from how many of the six levels (work, product line, objectives, strategy, principles, vision) are aligned, drifting or in conflict. It is an illustrative score, not a measured metric.
- **Flock behaviour:** each bird follows its seven nearest neighbours (as real starlings do), with soft separation and some wander. The flock's target path leans toward the star as alignment rises and away from it as alignment falls. At high alignment the flock occasionally splits in two and rejoins. Lower alignment is looser and more jumbled. The score is computed once at load; there is no live alignment control in the shipped page.
- **Flight path:** a stepper from work to the North Star, each stop coloured by its gap status and linking to its section.
- **Open questions:** shown as notes or cards, with decision maker and due date.

## Skins so far

| Skin | Look | Flock |
| --- | --- | --- |
| starling | Playful: grid paper, navy and yellow, sticky-note questions, journey stepper | Chevron birds |
| modern | Neutral canvas in Out of Owls brand colours, large type, segmented progress, post-it questions, Out of Owls logo top right with a "Brought to you by" tag, gradient green-amber-red status colours, star-dotted wordmark with a tagline, soft tonal-wash background, North Star top right | Chevron birds, no trails |

Two further skins (corporate, arcade) were tried and dropped.

`config.json` options: `title_tag`, `wordmark` (star-dotted "i"), `tagline`, `broughtBy`, `logo` (true shows the Out of Owls logo from `design/assets`), `title`, `lead`, `starLabel`, `birds` (`chevron`, `dot`, `pixel`), `dotR`, `alpha`, `colorVar`, `palette`, `trails`, `trailFade`.

## Adding a skin

1. Copy an existing folder under `design/skins/`.
2. Edit tokens, CSS and config. Define every colour as a token on `:root`; a dark variant redefines tokens only.
3. Run `python design/build.py` and open `design/dist/<name>.html`.

## Status colours

In the Modern skin the flight-path bars use a continuous green to amber to red gradient driven by a gap-severity score (0 aligned, 1 severe). Red appears only where severity is high. The scores in the sample are invented; in a real build they must come from a defined measure, not a judgement call.

## Notes

- The Starling skin was inspired by the feel of a playful retrospective tool (journey bar, sticky notes). It does not reuse that tool's artwork, layout or branding. The other three skins are independent of it.
- Desktop only for now. No phone layout has been designed or tested.
- Fonts load from Google Fonts. Offline, the page falls back to system fonts.
