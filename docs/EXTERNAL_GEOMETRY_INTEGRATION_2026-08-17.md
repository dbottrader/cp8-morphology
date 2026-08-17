# CP8 External Geometry Integration — 2026-08-17

Status: applied design contract on recovery branch

## Purpose
Convert external geometry research into a CP8-compatible calibration and promotion pipeline without importing unverified claims or unlicensed code.

## External findings mapped into CP8

### Geoparsing / GDP-29K
Reusable concept: parse diagrams into a formal geometry language before downstream reasoning. GDP-29K pairs plane/solid diagrams with ground-truth formal descriptions.
CP8 application: insert FORMALIZATION between REPRESENTATION and DECODING. A model output is not evidence until its formal description can be checked against measured primitives.

### GeoSym127K
Reusable concept: seeded grammar-based synthesis + exact symbolic ground truth + rendered diagrams.
CP8 application: generate deterministic positive/negative controls from an explicit seed and derivation grammar, then score morphology/model invariance against known ground truth.
Licensing note: no root LICENSE observed in the public repository during this audit; architecture may be studied, but source code is not copied into CP8 until licensing is resolved.

### Geoint-R1 / Geoint
Reusable concept: proof-backed geometry using Lean4 plus structured diagrams and auxiliary constructions.
CP8 application: add optional FORMAL_PROOF status above solver agreement. Promotion may use verified proof for geometry propositions when expressible.

### GeoSketch
Reusable concept: perception -> symbolic reasoning -> action -> updated perception loop.
CP8 application: transformations and auxiliary constructions become explicit TEST actions, never silent preprocessing. Each action must be in the receipt.

### GeoChallenge / GeomVerse / GeoPQA
Reusable concept: calibrated external benchmarks expose visual-perception and reasoning failure modes.
CP8 application: benchmark candidate models on known-answer geometry before using them on unknown crop-circle/glyph artifacts.

### GeoMathCode / GF-Reasoner
Reusable concept: programmatic/formal intermediate representations can be more reliable and inspectable than free-form visual reasoning.
CP8 application: prefer machine-checkable intermediate forms and solver outputs over narrative interpretations.

## Revised CP8 pipeline

ARTIFACT
-> HASH + METADATA
-> NORMALIZATION
-> PRIMITIVE MEASUREMENT
-> GRAPH REPRESENTATION
-> FORMALIZATION
-> DETERMINISTIC/SYMBOLIC CHECK
-> TRANSFORMATION TESTS
-> MODEL COMPARISON
-> CONTROL COMPARISON
-> OPTIONAL FORMAL PROOF
-> MACHINE RECEIPT
-> PROMOTION / REJECTION
-> INTERPRETATION

Interpretation is downstream of all measured and formal layers.

## Calibration strata

1. KNOWN: external geometry datasets with known annotations/answers.
2. SYNTHETIC: seeded CP8-generated controls with known construction grammar.
3. ADVERSARIAL: rotated/scaled/noisy/redrawn/occluded variants.
4. UNKNOWN: crop circles, petroglyphs, glyph artifacts, other research targets.

No method may be tuned on UNKNOWN and then presented as independently validated on that same set.

## Required component contract

Every external component must declare:
- component_id and version/revision
- source and license state
- claimed function
- CP8 stage it replaces or augments
- deterministic input identifiers and SHA-256 hashes
- parameters and random seeds
- known-answer benchmark result
- transformation/invariance result
- synthetic-control result
- failure cases
- output hash
- promotion decision and reasons

## Promotion gates

REJECT: execution failure, unknown provenance, hidden mutation, benchmark regression, or material invariance failure.
EXPERIMENTAL: executes and has receipts but is not yet independently reproduced or sufficiently calibrated.
VALIDATED_COMPONENT: passes known-answer calibration, controls, invariance thresholds, reproducible replay, and provenance checks.
PROOF_BACKED: validated component plus relevant machine-checked formal proof.

No Receipt = No Promotion.
Specification != Implementation.
Model Agreement != Ground Truth.
Interpretation != Measurement.

## Current repository-state discrepancy
README.md describes production modules (`cp8_morphology/geometry.py`, `graph.py`, `binary.py`, `fingerprint.py`, `synthetic.py`, `pipeline.py`, `cli.py`) totaling roughly 1,430 lines, but neither `main` nor the recovery branch currently contains those files. Until recovered, those modules are classified as DOCUMENTED/HISTORICAL CLAIMS, not present runtime implementation.

## Immediate executable target
The accompanying `tools/component_eval.py` implements a standard-library receipt evaluator. It does not pretend to perform geometry parsing itself; it provides the promotion gate into which recovered CP8 modules and external model/solver adapters must report.
