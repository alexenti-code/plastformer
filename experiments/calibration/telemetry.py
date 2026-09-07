#!/usr/bin/env python3
"""PlastFormer calibration -- content-blind telemetry over a stand episode.

Computes the proxy metrics of calibration/protocol.md v0.1 section 4 from:
  * the record store of an episode (organ-dataset acts format: records with
    id, record_tick, layer, act, refs, _fact_ids)
  * the biography ledger oracle (fact_id -> superseded_by, probe annotations)

Content-blind: this module reads ids, ticks, layers, act types and the
ledger's structure. It never reads record `content` (C2). The ledger oracle
is used post-hoc only and never enters the model's context (C7).

Pure stdlib. Deterministic.

Usage:
  python3 telemetry.py --acts ../organ-dataset/acts/bio-01.json \
                       --bio   ../organ-dataset/biographies/bio-01.json
"""

import argparse
import json
import math
from pathlib import Path

LAYERS = ["beat", "episode", "day", "project", "life"]

# Default tau set in ticks (executor defaults, gen_acts.py SPEC 3.2).
TAU_TICKS = {"beat": 10, "episode": 50, "day": 200,
             "project": 1000, "life": 5000}

DEFAULT_DIALS = {
    "audibility_floor": 0.01,
    "surfacing_cap": 12,
    "consolidation_ceiling": 8.0,
    "interference_factor": 1.0,
    **{f"tau_multiplier.{l}": 1.0 for l in LAYERS},
}


def amplitude(record, tick, dials):
    """Amplitude profile of one record at a given tick (THEORY: decay in
    lived ticks; dormancy = zero lived time). Multi-tau: the record lives on
    its chosen layer's tau; multipliers scale the tau set (the searchable
    dials). Content-blind: layers and ticks only."""
    tau = TAU_TICKS[record["layer"]] * dials[f"tau_multiplier.{record['layer']}"]
    dn = max(0, tick - record["record_tick"])
    return math.exp(-dn / tau)


def build_probe_index(bio, acts):
    """Map each probe to (target fact_id, probe message_no) and build the
    fact_id -> [record ids] index."""
    fid2recs = {}
    for r in acts["records"]:
        for f in r.get("_fact_ids", []):
            fid2recs.setdefault(f, []).append(r)
    probes = []
    for a in bio["annotations"]:
        k, ex = a["kind"], a.get("extra", {})
        if k == "probe_recall" and ex.get("target_fid"):
            probes.append({"msg": a["message_no"], "kind": k, "fid": ex["target_fid"]})
        elif k == "probe_position" and ex.get("chain"):
            # latest link of the chain is the current position
            probes.append({"msg": a["message_no"], "kind": k,
                           "chain": ex["chain"]})
        elif k == "probe_crossref" and ex.get("crossref_fid"):
            probes.append({"msg": a["message_no"], "kind": k, "fid": ex["crossref_fid"]})
        elif k == "probe_contradiction" and ex.get("contradiction"):
            # first_fid lives in extra (not inside the contradiction dict);
            # ledger convention: the second side is "C2:<first_fid>"
            first = ex.get("first_fid")
            probes.append({"msg": a["message_no"], "kind": k,
                           "fid": first,
                           "v2_fid": f"C2:{first}" if first else None})
    return probes, fid2recs


def tick_at_message(acts, message_no):
    """Stand tick as of a message_no (timeline is sequential)."""
    t = 0
    for e in acts["timeline"]:
        if e["message_no"] >= message_no:
            break
        for ph in e.get("phases", []):
            p = ph.get("payload") or {}
            t = max(t, p.get("tick", t))
    return t


def metrics(acts, bio, dials=None):
    """Compute recall / stale_wins / window_cost / economy for one episode."""
    dials = {**DEFAULT_DIALS, **(dials or {})}
    floor = dials["audibility_floor"]
    cap = dials["surfacing_cap"]
    records = acts["records"]
    probes, fid2recs = build_probe_index(bio, acts)

    recall_hits = recall_total = 0
    stale_wins = 0
    surfaced_counts = []
    needed_counts = []

    for p in probes:
        t = tick_at_message(acts, p["msg"])

        def amp(r):
            return amplitude(r, t, dials)

        # All records alive at the probe tick (surfacing candidates).
        alive = [r for r in records if r["record_tick"] <= t]
        ranked = sorted(alive, key=amp, reverse=True)
        audible = [r for r in ranked if amp(r) >= floor][:cap]

        if p["kind"] in ("probe_recall", "probe_crossref"):
            fid = p["fid"]
            targets = [r for r in fid2recs.get(fid, []) if r["record_tick"] <= t]
            if not targets:
                continue
            recall_total += 1
            best = max(amp(r) for r in targets)
            if best >= floor:
                recall_hits += 1
            # stale check: does a superseded (earlier) record out-amplify
            # its replacement?
            if len(targets) > 1:
                targets_by_tick = sorted(targets, key=lambda r: r["record_tick"])
                newest = targets_by_tick[-1]
                older = targets_by_tick[:-1]
                if best >= floor and max(amp(r) for r in older) > amp(newest):
                    stale_wins += 1
            needed_counts.append(len(targets))
        elif p["kind"] == "probe_position":
            # chain: [old value, ..., current value]; the CURRENT link must
            # win; an out-amplified older link is a stale win by physics.
            chain = p["chain"]
            fids = [link["lid"] for link in chain if link.get("lid") in fid2recs]
            if not fids:
                continue
            recall_total += 1
            per_link = {f: max((amp(r) for r in fid2recs[f] if r["record_tick"] <= t),
                               default=0.0) for f in fids}
            current = fids[-1]
            if per_link[current] >= floor:
                recall_hits += 1
            if any(per_link[f] > per_link[current] for f in fids[:-1]):
                stale_wins += 1
            needed_counts.append(1)
        elif p["kind"] == "probe_contradiction":
            # review 4.2: BOTH sides of a contradiction must be surfaceable
            # (PR10 weighing behavior). Each side scores separately; the
            # probe counts toward recall only if BOTH sides are audible.
            sides = [f for f in (p.get("fid"), p.get("v2_fid")) if f]
            side_ok = []
            for f in sides:
                targets = [r for r in fid2recs.get(f, []) if r["record_tick"] <= t]
                if not targets:
                    side_ok = None
                    break
                side_ok.append(max(amp(r) for r in targets) >= floor)
            if side_ok is None or not sides:
                continue
            recall_total += 1
            needed_counts.append(2 * len(sides))
            if all(side_ok):
                recall_hits += 1

        surfaced_counts.append(len(audible))

    n_probes = max(1, len(needed_counts))
    mean_needed = sum(needed_counts) / n_probes
    window_cost = (sum(surfaced_counts) / max(1, len(surfaced_counts))) - mean_needed
    write_acts = sum(1 for r in records if r["act"] in
                     ("name", "repeat", "connect", "reconcile"))
    economy = write_acts / n_probes

    m = {
        "recall": recall_hits / max(1, recall_total),
        "recall_total": recall_total,
        "stale_wins": stale_wins,
        "window_cost": max(0.0, window_cost),
        "economy": economy,
    }
    m["S"] = (1.0 * m["recall"] - 0.6 * m["stale_wins"] / max(1, m["recall_total"])
              - 0.15 * m["window_cost"] - 0.10 * m["economy"])
    m["n_probes"] = n_probes
    return m


# ---- died_too_early: the offline report consumed by the core (`calibrate`
# evidence). Content-blind: record ids and ticks only. -------------------

def died_too_early(acts, bio, dials=None, horizon_after_end=50):
    """Records whose amplitude fell below the floor by the end of the
    episode + horizon, on a layer where they should have outlived it
    (layer tau > time elapsed). Signals tau too fast / floor too high."""
    dials = {**DEFAULT_DIALS, **(dials or {})}
    final_tick = acts.get("final_tick", max(r["record_tick"] for r in acts["records"]))
    out = []
    for r in acts["records"]:
        tau = TAU_TICKS[r["layer"]] * dials[f"tau_multiplier.{r['layer']}"]
        a = amplitude(r, final_tick + horizon_after_end, dials)
        if a < dials["audibility_floor"] and horizon_after_end < tau:
            out.append({"record_id": r["id"], "layer": r["layer"],
                        "amplitude": round(a, 4), "metric": "died_too_early"})
    return out


def report(acts, bio, dials=None):
    """Offline diagnostics artifact (stand/harness side).

    NOT a PMI block and never serialized as one: PMI carries only the
    instance's own records in response to the model's own `read`.
    The oracle-derived metrics below (recall, stale_wins, window_cost,
    economy, S) stay harness-side (C7); the only physics-only channel
    admissible near the core is `died_too_early` (amplitudes/ticks, no
    oracle). Feeding any oracle-derived metric to the core requires a
    separate owner adjudication in protocol.md (Channel note)."""
    m = metrics(acts, bio, dials)
    dte = died_too_early(acts, bio, dials)
    return {"metrics": {k: round(v, 4) if isinstance(v, float) else v
                        for k, v in m.items()},
            "died_too_early": dte[:20],
            "content_blind": True,
            "channel": "offline-diagnostics/harness-only"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts", required=True)
    ap.add_argument("--bio", required=True)
    ap.add_argument("--floor", type=float, default=None)
    args = ap.parse_args()
    acts = json.load(open(args.acts))
    bio = json.load(open(args.bio))
    dials = {"audibility_floor": args.floor} if args.floor else None
    print(json.dumps(report(acts, bio, dials), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
