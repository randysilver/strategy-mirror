#!/usr/bin/env python3
"""Turn an onboarding profile's claims into a Starling data file.

Usage:  python design/claims_to_data.py PROFILE.yaml [--out client/data/draft.json] [--today YYYY-MM-DD]
        python design/build.py --data client/data/draft.json

PROFILE may be YAML (needs PyYAML) or JSON. Output shape: docs/DATA_MODEL.md.
Mirror rules: every non-rejected claim is kept as a best guess; confidence, flags, alternatives and
source quotes are carried over; an item counts as reviewed only when status is reviewed_ok or edited
AND reviewed_by_role is set. Rejected claims are dropped and reported. Prints a report; exit 1 on
problems that stop the page from working (no strategies, duplicate or malformed IDs).
"""
import datetime, json, pathlib, re, sys

FLAGS = {"conflict", "low_confidence", "single_source", "stale", "no_owner", "unclear"}
STATUS = {"on": "on", "on_track": "on", "risk": "risk", "at_risk": "risk"}
STORE = {"google_sheets": "Google Sheets", "excel_sharepoint": "Excel", "airtable": "Airtable", "sql_database": "Database"}
USED = {"model.vision", "model.objectives", "model.strategies", "model.goals", "model.opportunities", "work.initiatives",
        "sources.inventory", "cadence.horizon", "roles.owner", "scope.description"}
CROSSCHECK = {"work.unlinked"}


def load(path):
    p = pathlib.Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML is needed for YAML input (pip install pyyaml), or pass a JSON file.")
    return yaml.safe_load(text) or {}


def many(v):
    return v if isinstance(v, list) else [v]


def clean(d):
    return {k: v for k, v in d.items() if v is not None}


def sval(v):
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)


def num(v, default=None):
    try:
        return int(v) if float(v) == int(float(v)) else float(v)
    except (TypeError, ValueError):
        return default


def norm_split(sp):
    """Page wants fractions that add up to 1. Accept percentages (60/40) or fractions (0.6/0.4)."""
    if not isinstance(sp, dict) or not sp:
        return None
    vals = {str(k): float(v) for k, v in sp.items() if num(v) is not None}
    return {k: round(v / 100, 4) for k, v in vals.items()} if sum(vals.values()) > 1.5 else vals


def short_name(alias):
    """'Tesco PLC (public sources)' -> 'Tesco'. Used in page copy: 'how Tesco contributes', 'Tesco's work'."""
    if not alias:
        return None
    n = re.sub(r"\s*\([^)]*\)", "", str(alias)).strip()
    n = re.sub(r"[ ,]+(plc|ltd|limited|inc\.?|llc)$", "", n, flags=re.I).strip()
    return n or None


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        sys.exit(__doc__)
    src = args[0]
    out = pathlib.Path(args[args.index("--out") + 1]) if "--out" in args else pathlib.Path("client/data/draft.json")
    today = args[args.index("--today") + 1] if "--today" in args else datetime.date.today().isoformat()
    prof = load(src)
    claims = prof.get("claims") or []
    rep = {"errors": [], "warnings": [], "dropped": [], "unused": {}, "counts": {}}

    def warn(m): rep["warnings"].append(m)
    def err(m): rep["errors"].append(m)

    # ---- provenance carried onto an item
    def prov(c, label):
        d = {}
        if c.get("confidence") in ("high", "medium", "low"):
            d["conf"] = c["confidence"]
        fl = [f for f in (c.get("flags") or []) if f in FLAGS]
        for f in (c.get("flags") or []):
            if f not in FLAGS:
                warn(f"{c.get('id')}: unknown flag '{f}' ignored")
        if fl:
            d["flags"] = fl
        alts = [{"value": sval(a.get("value")), "source": ", ".join(x for x in (a.get("source_id"), a.get("locator")) if x)} for a in (c.get("alternatives") or [])]
        if alts:
            d["alternatives"] = alts
        srcs = [clean({"source": s.get("source_id"), "locator": s.get("locator"), "quote": s.get("quote")}) for s in (c.get("sources") or [])]
        if srcs:
            d["sources"] = srcs
        if c.get("status") in ("reviewed_ok", "edited"):
            if c.get("reviewed_by_role"):
                d["reviewed"] = clean({"by": c["reviewed_by_role"], "on": str(c["date"]) if c.get("date") else None})
            else:
                warn(f"{c.get('id')} ({label}): status {c['status']} but no reviewed_by_role, so it shows as unreviewed")
        return d

    by_field = {}
    for c in claims:
        if c.get("status") == "rejected":
            rep["dropped"].append(f"{c.get('id')} ({c.get('field')}): rejected" + (f", {c['note']}" if c.get("note") else ""))
            continue
        by_field.setdefault(c.get("field"), []).append(c)
    for f, cs in by_field.items():
        if f not in USED and f not in CROSSCHECK:
            rep["unused"][f] = len(cs)

    def items(field):
        for c in by_field.get(field, []):
            for v in many(c.get("value")):
                if isinstance(v, dict):
                    yield c, v
                else:
                    warn(f"{c.get('id')}: {field} value is not an object, skipped")

    # ---- objectives
    objectives, seen = [], set()
    def uniq(kind, i):
        if not i:
            err(f"a {kind} has no id")
            return False
        if re.search(r"[:|]", str(i)) or str(i) == "none":
            err(f"{kind} id '{i}' must not contain ':' or '|' and must not be 'none'")
            return False
        if (kind, i) in seen:
            err(f"duplicate {kind} id '{i}'")
            return False
        seen.add((kind, i))
        return True
    for c, v in items("model.objectives"):
        if uniq("objective", v.get("id")):
            objectives.append(clean({"id": str(v["id"]), "name": v.get("name") or str(v["id"]), "owner": v.get("owner"), **prov(c, "objective")}))

    # ---- strategies, goals, opportunities
    strategies, SB = [], {}
    for c, v in items("model.strategies"):
        if not uniq("strategy", v.get("id")):
            continue
        succ = v.get("success")
        if isinstance(succ, dict):
            succ = clean({"m": succ.get("name") or succ.get("m"), "t": succ.get("target") or succ.get("t"), "by": sval(succ.get("target_year") or succ.get("by")) if (succ.get("target_year") or succ.get("by")) else None, "kind": succ.get("kind", "outcome")})
        elif succ:
            succ = {"m": str(succ), "by": None, "kind": "outcome"}
        s = clean({"id": str(v["id"]), "name": v.get("name") or str(v["id"]), "status": STATUS.get(str(v.get("status", "")).lower().replace(" ", "_"), "na"),
                   "stated": num(v.get("stated_fte", v.get("stated")), 0), "objs": [str(o) for o in (v.get("objectives") or v.get("objs") or [])],
                   "success": succ or None, "owner": v.get("owner"), "goals": [], "opps": [], **prov(c, "strategy")})
        strategies.append(s); SB[s["id"]] = s
    for c, v in items("model.goals"):
        sid = str(v.get("strategy") or v.get("strat") or "")
        if sid not in SB:
            err(f"goal {v.get('id')}: strategy '{sid}' is not in the strategies"); continue
        if not uniq("goal", v.get("id")):
            continue
        ms = [clean({"m": m.get("name") or m.get("m"), "t": m.get("target") or m.get("t"), "by": str(m.get("target_year") or m.get("by")) if (m.get("target_year") or m.get("by")) else None, "kind": m.get("kind", "outcome")}) for m in (v.get("measures") or [])]
        for m in ms: m.setdefault("by", None)
        measured = bool(v["measured"]) if "measured" in v else any(m.get("current") for m in (v.get("measures") or []))
        SB[sid]["goals"].append(clean({"id": str(v["id"]), "name": v.get("name") or str(v["id"]), "strat": sid, "measured": measured, "measures": ms, "owner": v.get("owner"), **prov(c, "goal")}))
    for c, v in items("model.opportunities"):
        sid = str(v.get("strategy") or v.get("strat") or "")
        if sid not in SB:
            err(f"opportunity {v.get('id')}: strategy '{sid}' is not in the strategies"); continue
        if not uniq("opportunity", v.get("id")):
            continue
        SB[sid]["opps"].append(clean({"id": str(v["id"]), "name": v.get("name") or str(v["id"]), "goal": str(v["goal"]) if v.get("goal") else None, "strat": sid, "owner": v.get("owner"), **prov(c, "opportunity")}))
    if not strategies:
        err("no model.strategies claims, so there is nothing to show")

    # ---- roles.owner
    for c, v in items("roles.owner"):
        tid, owner = str(v.get("id") or v.get("item") or ""), v.get("owner")
        hit = SB.get(tid) or next((x for x in objectives if x["id"] == tid), None) or next((g for s in strategies for g in s["goals"] if g["id"] == tid), None) or next((o for s in strategies for o in s["opps"] if o["id"] == tid), None)
        if hit and owner:
            hit["owner"] = owner
        else:
            warn(f"{c.get('id')}: roles.owner needs {{id, owner}} for an item that exists; skipped")

    # ---- horizon
    quarters, horizon = None, None
    for c, v in items("cadence.horizon"):
        if v.get("quarters"):
            quarters = [clean({"label": q.get("label"), "year": num(q.get("year"))}) for q in v["quarters"]]
        if v.get("horizon"):
            horizon = v["horizon"]
    # ---- initiatives
    inits = []
    for c, v in items("work.initiatives"):
        if not uniq("initiative", v.get("id")):
            continue
        links = [clean({"strat": str(l["strategy"]) if l.get("strategy") else None, "goal": str(l["goal"]) if l.get("goal") else None, "opp": str(l["opportunity"]) if l.get("opportunity") else None}) for l in (v.get("links") or [])]
        for l in links:
            for k in ("strat", "goal", "opp"): l.setdefault(k, None)
        q = [num(x, 0) for x in (v.get("fte_by_quarter") or v.get("q") or [])]
        first = links[0] if links else {}
        if "funded" not in v or v["funded"] is None:
            warn(f"initiative {v['id']}: funded is unknown, shown as unfunded")
        trk = v.get("tracker") if isinstance(v.get("tracker"), dict) else None
        inits.append(clean({"id": str(v["id"]), "name": v.get("name") or str(v["id"]), "strat": first.get("strat"), "goal": first.get("goal"), "opp": first.get("opp"), "links": links,
            "split": norm_split(v.get("split")), "fte": num(v.get("fte"), max(q) if q else 0), "q": q, "funded": bool(v.get("funded")), "ws": v.get("workstream"),
            "disc": bool(v.get("discretionary")), "benef": v.get("beneficiary") or "Not recorded", "jira": trk, "com": num(v.get("commitments"), 0),
            "comRisk": num(v.get("commitments_at_risk"), 0), "capSens": bool(v.get("capacity_sensitive")), "owner": v.get("owner"), **prov(c, "initiative")}))
    nq = max([len(i["q"]) for i in inits] + [len(quarters or [])] or [0])
    if not quarters:
        yr = int(today[:4]); quarters = [{"label": f"Period {n+1}", "year": yr} for n in range(nq)]
        if inits:
            warn("no cadence.horizon claim with quarters: periods are labelled Period 1..n, all in the current year. Add one so the roadmap shows real quarters")
    for i in inits:
        i["q"] = (i["q"] + [0] * len(quarters))[:len(quarters)]
    if not horizon:
        horizon = {"label": "planning period", "from": 0, "to": max(0, len(quarters) - 1)}
        if inits:
            warn("no horizon given: the whole period is averaged")
    # cross-check unlinked
    stated_unl = {str(x.get("id")) for c, x in items("work.unlinked")}
    actual_unl = {i["id"] for i in inits if not any(l.get("strat") for l in i["links"])}
    if stated_unl and stated_unl != actual_unl:
        warn(f"work.unlinked lists {len(stated_unl)} initiatives but {len(actual_unl)} have no strategy in work.initiatives; the page uses the links")

    # ---- sources -> claimDocs
    claimdocs = []
    for c, v in items("sources.inventory"):
        sid = str(v.get("id") or v.get("source_id") or "")
        cited = [k for k in claims if any(s.get("source_id") == sid for s in (k.get("sources") or []))]
        claimdocs.append({"id": sid, "kind": v.get("kind") or "Source", "n": len(cited), "conflicts": sum(1 for k in cited if "conflict" in (k.get("flags") or []))})
    # ---- open items -> questions
    questions = [{"id": f"Q{n+1}", "cat": (o.get("flags") or ["Review"])[0].replace("_", " ").capitalize(), "t": o.get("question") or f"Review {o.get('claim_id')}",
                  "why": "Flagged: " + ", ".join((o.get("flags") or [])) if o.get("flags") else "", "dm": o.get("reviewer_role") or "Not assigned"} for n, o in enumerate(prof.get("open_items") or [])]
    ds = (prof.get("technical") or {}).get("data_store") or {}
    meta_in = prof.get("meta") or {}
    sc = next((c for c in by_field.get("scope.description", [])), None)
    d = {"schema": "starling-data/1",
         "meta": clean({"org": meta_in.get("client_alias") or "Client", "team": meta_in.get("team") or short_name(meta_in.get("client_alias")) or "Team", "teamFull": (sc.get("value") if sc and isinstance(sc.get("value"), str) else None) or meta_in.get("client_alias") or "Team",
                        "snapshot": (lambda t: f"{t.day} {t.strftime('%b %Y')}")(datetime.date.fromisoformat(today)), "sources": len(claimdocs), "claims": len(claims), "built": today}),
         "text": clean({"source": STORE.get(ds.get("chosen")) or ds.get("chosen")}),
         "quarters": quarters, "horizon": horizon,
         "vision": next((sval(v) for c in by_field.get("model.vision", []) for v in many(c.get("value"))), ""),
         "objectives": objectives, "strategies": strategies, "initiatives": inits, "pilot": [], "questions": questions,
         "changes": [], "claimDocs": claimdocs, "modelChecks": [], "otherDecisions": []}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- report
    allitems = objectives + strategies + [g for s in strategies for g in s["goals"]] + [o for s in strategies for o in s["opps"]] + inits
    fl = {}
    for x in allitems:
        for f in x.get("flags", []): fl[f] = fl.get(f, 0) + 1
    print(f"Wrote {out}  ({len(claims)} claims read)")
    print(f"  objectives {len(objectives)} · strategies {len(strategies)} · goals {sum(len(s['goals']) for s in strategies)} · opportunities {sum(len(s['opps']) for s in strategies)} · initiatives {len(inits)}")
    print(f"  reviewed {sum(1 for x in allitems if x.get('reviewed'))} · flagged {sum(1 for x in allitems if x.get('flags'))}" + (" (" + ", ".join(f"{k} {v}" for k, v in sorted(fl.items())) + ")" if fl else ""))
    print(f"  unlinked initiatives {len(actual_unl)} · open questions from open_items {len(questions)}")
    for k, lst in (("Dropped", rep["dropped"]), ("Warnings", rep["warnings"]), ("Errors", rep["errors"])):
        if lst:
            print(f"{k}:"); [print("  - " + m) for m in lst]
    if rep["unused"]:
        print("Not used by the page (kept in the profile): " + ", ".join(f"{k} ({n})" for k, n in sorted(rep["unused"].items())))
    sys.exit(1 if rep["errors"] else 0)


if __name__ == "__main__":
    main()
