# CP8 Morphology Lab

**Formation Morphology Toolkit — Pass 0–6**

Domain-agnostic computational morphology engine for aerial crop circles, petroglyphs, synthetic patterns, and CAD geometries.

Part of the **ASIN-HHC / CP8** ecosystem (USPTO Provisional #63/892,035).

Glyph signature: ❖𓂀∞CP8⟡⚯◇

---

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# CLI
cp8-morphology formation.jpg --resolution 0.15 --output genome.json --overlay viz.png

# Python
from cp8_morphology import run_pipeline
genome = run_pipeline("formation.jpg", pixel_resolution_m=0.15)
```

---

## Package Structure

```
cp8-morphology/
├── README.md
├── LICENSE                      # Proprietary — ASIN-HHC LLC
├── setup.py
├── requirements.txt
├── .gitignore
├── push_to_github.sh
│
├── cp8_morphology/
│   ├── __init__.py
│   ├── geometry.py              # Pass 0-1: Image → primitives
│   ├── graph.py                 # Pass 2: Graph construction
│   ├── binary.py                # Pass 3: Binary hypothesis scanner
│   ├── fingerprint.py           # Pass 5: 5-submetric fingerprints
│   ├── synthetic.py             # 4-generator control library
│   ├── pipeline.py              # Pass 0-6 integration
│   └── cli.py                   # Command-line interface
│
├── examples/
│   └── crabwood_face_genome.json
├── tests/
└── docs/
```

---

## Modules (Production)

| Module | Pass | Lines | Status |
|--------|------|-------|--------|
| `geometry.py` | 0-1 | ~400 | ✅ |
| `graph.py` | 2 | ~200 | ✅ |
| `binary.py` | 3 | ~180 | ✅ |
| `fingerprint.py` | 5 | ~250 | ✅ |
| `synthetic.py` | Controls | ~200 | ✅ |
| `pipeline.py` | Integration | ~120 | ✅ |
| `cli.py` | CLI | ~80 | ✅ |
| **Total** | | **~1,430** | |

---

## Key Design Principles

- **Domain-agnostic** — works on crop circles, petroglyphs, synthetic patterns, CAD
- **Reproducible** — every measurement carries provenance, versions, parameters
- **Extensible** — add new Pass 5 sub-metrics without changing the schema
- **Honest** — simulated results are labeled; binary claims require cross-formation validation
- **Schema-aligned** — matches the ASIN-HHC / CP8 Glyph Artifact Schema

---

## Critical Notes (v1.0.0)

- Binary detection currently triggers on multiple synthetic controls. Pass 3 rejection criteria require tightening (cross-formation consistency) before encoding claims.
- Ring detection is sensitive to perspective distortion in aerial imagery.
- No ground-truth physical measurements; all scales are estimates.

---

## Related

- [CP8-Ultimate-System](https://github.com/dbottrader/CP8-Ultimate-System) — Build summary & results
- ASIN-HHC ecosystem repositories

**License**: Proprietary — ASIN-HHC LLC
