# OpenRoot Canon

Locked language. Locked algorithms. Newton chain.

You have been explaining the same five laws in a hundred READMEs. That is weed. This repo is the one trunk.

```
canon/CANON.json           N00–N15. Do not paraphrase.
canon/NOMENCLATURE.json    one token, one meaning
canon/ALGORITHMS.json      index of functions
canon/CANDIDATES.json      born only from need_gate
src/canon.py               the only evaluator
```

## How to speak

Cite an id. Do not rewrite the sentence.

- η is N01
- Γ is N02
- C(N,T,R) is N03
- the diary is N10
- a new word is N11

If you feel a paragraph coming on, run Newton first:

```bash
python3 /sdcard/openroot/canon/src/canon.py newton "what is gamma"
python3 /sdcard/openroot/canon/src/canon.py derive "should I put this on Solana"
python3 /sdcard/openroot/canon/src/canon.py eval coord --N 36 --T 2 --R 1.0
python3 /sdcard/openroot/canon/src/canon.py eval gamma --Y 20 --L 1 --P 10 --F 5 --Jh 0.5 --Je 0 --C 0
```

R=1.0 must print `0.0` for coord when T>=1. If it does not, the file is corrupt.

## How a new word is allowed to exist

1. Search tokens. If one already says it, stop.
2. `python3 src/canon.py need TOKEN "one sentence meaning"`
3. The token stays a candidate until it has 3 real uses.
4. Then you add it to NOMENCLATURE.json by hand and hang the file on the thermo chain.
5. You never grow CANON.json because a chat was long.

Need is the only expansion energy. Curiosity essays are compost, not canon.

## What this is not

Not the thermo ledger (that is `thermo-lattice`).  
Not AeroCement calc.  
Not the statue module.  
Those hang *from* these names. They do not rename them.

## Hang

After genesis of `/sdcard/openroot/thermo`:

```bash
python3 /sdcard/openroot/thermo/src/thermo_ledger.py hang \
  /sdcard/openroot/canon/canon/CANON.json \
  --what CANON --note "N00-N15 locked" \
  --root /sdcard/openroot/thermo
```

When CANON.json changes, the hash changes, a new block appears. The old blob remains. That is how you see that you broke a lock.

## Knowledge Integration
See `docs/knowledge/`.
