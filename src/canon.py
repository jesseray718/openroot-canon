#!/usr/bin/env python3
"""
OpenRoot Canon — locked names and algorithms.
Newton chain: match a postulate, skip the essay.
Need-gate: a new word is expensive.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

K_BOLTZMANN = 1.380649e-23
ROOT = Path(__file__).resolve().parents[1]
CANON_PATH = ROOT / "canon" / "CANON.json"
NOM_PATH = ROOT / "canon" / "NOMENCLATURE.json"
ALG_PATH = ROOT / "canon" / "ALGORITHMS.json"
CANDIDATE_PATH = ROOT / "canon" / "CANDIDATES.json"


def load() -> tuple[dict, dict, dict]:
    canon = json.loads(CANON_PATH.read_text(encoding="utf-8"))
    nom = json.loads(NOM_PATH.read_text(encoding="utf-8"))
    alg = json.loads(ALG_PATH.read_text(encoding="utf-8"))
    return canon, nom, alg


def candidates() -> dict:
    if not CANDIDATE_PATH.exists():
        return {"version": "1.0.0", "items": {}}
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def save_candidates(obj: dict) -> None:
    tmp = CANDIDATE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(CANDIDATE_PATH)


def coord(N: float, T: float, R: float) -> float:
    if R >= 1.0 and T >= 1:
        return 0.0
    return N * 0.001 * (1 + 0.1 * T) * ((1 - R) ** T)


def synergy(N: float, R: float, B: float = 6.0) -> float:
    if N <= 0 or B <= 1:
        raise ValueError("N>0 and B>1")
    return 1.0 + (R * 0.5 * (math.log(N) / math.log(B)))


def eta(useful_joules: float, human_joules: float) -> float | None:
    if human_joules <= 0:
        return None
    return useful_joules / human_joules


def gamma(Y: float, L: float, P: float, F: float, Jh: float, Je: float, C: float) -> float | None:
    den = Jh + Je + C
    if den <= 0:
        return None
    return (Y * L * P * F) / den


def landauer(bits: float, T_kelvin: float = 300.0) -> float:
    return bits * T_kelvin * K_BOLTZMANN * math.log(2)


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _postulate(canon: dict, pid: str) -> dict | None:
    for p in canon["postulates"]:
        if p["id"] == pid or p["name"] == pid:
            return {"id": p["id"], "name": p["name"], "lock": p["lock"]}
    return None


def newton(query: str, canon: dict, nom: dict) -> list[dict]:
    q = _norm(query)
    hits = []
    for word in q.split():
        target = nom.get("redirects", {}).get(word)
        if target:
            if target.startswith("N"):
                h = _postulate(canon, target)
                if h:
                    hits.append(h)
            elif target in nom["tokens"]:
                hits.append({"id": "NOM", "name": target, "lock": nom["tokens"][target]})
    for p in canon["postulates"]:
        blob = _norm(p["id"] + " " + p["name"] + " " + p.get("symbol", "") + " " + p["lock"])
        keys = {p["id"].lower(), p["name"].lower(), p.get("symbol", "").lower()}
        if any(k and k in q.split() for k in keys) or any(tok in q for tok in keys if len(tok) > 2):
            hits.append({"id": p["id"], "name": p["name"], "lock": p["lock"]})
            continue
        # light overlap on distinctive words from the lock
        if p["name"] in q or p["id"].lower() in q:
            hits.append({"id": p["id"], "name": p["name"], "lock": p["lock"]})
    for token, meaning in nom["tokens"].items():
        tl = token.lower()
        if tl in q.split() or f" {tl} " in f" {q} ":
            already = {h["name"] for h in hits} | {h["id"] for h in hits}
            if token not in already and tl not in {h["name"].lower() for h in hits}:
                hits.append({"id": "NOM", "name": token, "lock": meaning})
    # unique by lock text
    seen = set()
    out = []
    for h in hits:
        if h["lock"] in seen:
            continue
        seen.add(h["lock"])
        out.append(h)
    return out


def need_gate(proposed: str, meaning: str, canon: dict, nom: dict) -> dict:
    prop = proposed.strip()
    key = _norm(prop)
    meaning_n = _norm(meaning)
    for p in canon["postulates"]:
        if key in _norm(p["name"] + " " + p.get("symbol", "") + " " + p["lock"]) or meaning_n in _norm(p["lock"]):
            return {"decision": "reuse", "cite": p["id"], "lock": p["lock"]}
    for token, m in nom["tokens"].items():
        if key == _norm(token) or key in _norm(m) or meaning_n in _norm(m):
            return {"decision": "reuse", "cite": token, "lock": m}
    for phrase in nom["forbidden_paraphrase"]:
        if _norm(phrase) in meaning_n or meaning_n in _norm(phrase):
            return {"decision": "reject", "reason": "forbidden_paraphrase", "phrase": phrase}
    c = candidates()
    item = c["items"].setdefault(
        prop,
        {"token": prop, "meaning": meaning, "uses": 0, "status": "candidate"},
    )
    item["uses"] = int(item.get("uses", 0)) + 1
    if item["uses"] >= 3:
        item["status"] = "ready_to_lock"
    c["items"][prop] = item
    save_candidates(c)
    return {
        "decision": "candidate",
        "token": prop,
        "uses": item["uses"],
        "status": item["status"],
        "rule": "3 real uses then lock into NOMENCLATURE.json by hand. Canon files stay small.",
    }


def derive(utterance: str, canon: dict, nom: dict) -> dict:
    hits = newton(utterance, canon, nom)
    if hits:
        return {"operator": "A1", "path": "Newton", "hits": hits}
    return {
        "operator": "A1",
        "path": "underived",
        "utterance": utterance,
        "next": "need_gate if this must become a token, else speak an existing one",
    }


def cmd_eval(args: argparse.Namespace) -> int:
    if args.fn == "coord":
        print(coord(args.N, args.T, args.R))
    elif args.fn == "synergy":
        print(synergy(args.N, args.R, args.B))
    elif args.fn == "eta":
        print(eta(args.useful, args.human))
    elif args.fn == "gamma":
        print(gamma(args.Y, args.L, args.P, args.F, args.Jh, args.Je, args.C))
    elif args.fn == "landauer":
        print(landauer(args.bits, args.Tkelvin))
    else:
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    canon, nom, _alg = load()
    p = argparse.ArgumentParser(description="OpenRoot canon")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("newton", help="match locked postulates, skip the essay")
    n.add_argument("query")

    d = sub.add_parser("derive", help="A1: Newton first")
    d.add_argument("utterance")

    g = sub.add_parser("need", help="propose a new token")
    g.add_argument("token")
    g.add_argument("meaning")

    sub.add_parser("list", help="print locked ids")
    sub.add_parser("tokens", help="print nomenclature tokens")

    e = sub.add_parser("eval", help="run a locked algorithm")
    e.add_argument("fn", choices=["coord", "synergy", "eta", "gamma", "landauer"])
    e.add_argument("--N", type=float, default=6)
    e.add_argument("--T", type=float, default=1)
    e.add_argument("--R", type=float, default=1.0)
    e.add_argument("--B", type=float, default=6)
    e.add_argument("--useful", type=float, default=0)
    e.add_argument("--human", type=float, default=0)
    e.add_argument("--Y", type=float, default=0)
    e.add_argument("--L", type=float, default=1)
    e.add_argument("--P", type=float, default=1)
    e.add_argument("--F", type=float, default=1)
    e.add_argument("--Jh", type=float, default=0)
    e.add_argument("--Je", type=float, default=0)
    e.add_argument("--C", type=float, default=0)
    e.add_argument("--bits", type=float, default=1)
    e.add_argument("--Tkelvin", type=float, default=300.0)

    args = p.parse_args(argv)
    if args.cmd == "newton":
        print(json.dumps(newton(args.query, canon, nom), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "derive":
        print(json.dumps(derive(args.utterance, canon, nom), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "need":
        print(json.dumps(need_gate(args.token, args.meaning, canon, nom), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "list":
        print(json.dumps([{k: p[k] for k in ("id", "name") if k in p} | {"symbol": p.get("symbol")} for p in canon["postulates"]], indent=2))
        return 0
    if args.cmd == "tokens":
        print(json.dumps(nom["tokens"], indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "eval":
        return cmd_eval(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
