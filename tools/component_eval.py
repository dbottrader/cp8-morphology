#!/usr/bin/env python3
"""CP8 component evaluation gate.

Consumes a JSON receipt emitted by any external/internal component adapter and
returns a deterministic promotion decision. Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

REQUIRED = [
    "component_id", "revision", "source", "license_state", "cp8_stage",
    "input_sha256", "output_sha256", "benchmark", "invariance", "controls",
    "replay", "claim_class", "observer_context",
]

CLAIM_CLASSES = {
    "OBSERVED", "MEASURED", "MATHEMATICAL_CORRESPONDENCE", "PHYSICAL_MECHANISM",
    "ANALOGY", "HYPOTHESIS", "SPECULATION",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(receipt: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for key in REQUIRED:
        if key not in receipt:
            errors.append(f"missing:{key}")

    for key in ("input_sha256", "output_sha256"):
        value = receipt.get(key, "")
        if not isinstance(value, str) or len(value) != 64:
            errors.append(f"invalid_sha256:{key}")

    if receipt.get("license_state") not in {
        "permissive", "compatible", "unknown", "restricted", "internal",
    }:
        errors.append("invalid:license_state")

    if receipt.get("claim_class") not in CLAIM_CLASSES:
        errors.append("invalid:claim_class")

    observer = receipt.get("observer_context")
    if not isinstance(observer, dict):
        errors.append("invalid:observer_context")
    else:
        for key in ("instrument_or_model", "frame"):
            if not observer.get(key):
                errors.append(f"missing:observer_context.{key}")

    for section in ("benchmark", "invariance", "controls", "replay"):
        if section in receipt and not isinstance(receipt[section], dict):
            errors.append(f"invalid_section:{section}")
    return errors


def metric_pass(section: Dict[str, Any]) -> bool:
    return section.get("pass") is True


def module_gates(receipt: Dict[str, Any]) -> List[str]:
    """Return module-specific failures. Absence is not success."""
    reasons: List[str] = []
    stage = receipt.get("cp8_stage")

    if stage == "TOPOLOGY":
        topology = receipt.get("topology", {})
        if topology.get("deformation_invariant") is not True:
            reasons.append("topology_deformation_invariance_not_established")

    if stage == "PROCESS_MODEL":
        process = receipt.get("process_genome", {})
        if process.get("known") is not True or not process.get("operations"):
            reasons.append("process_genome_incomplete")

    if stage == "LATTICE_CLASSIFICATION":
        lattice = receipt.get("lattice", {})
        if not lattice.get("class"):
            reasons.append("lattice_class_missing")
        confidence = lattice.get("confidence")
        if not isinstance(confidence, (int, float)) or confidence < 0.8:
            reasons.append("lattice_confidence_below_gate")

    if stage == "RESONANCE_MORPHOLOGY":
        driver = receipt.get("dynamic_driver", {})
        if driver.get("family") in {None, "none"}:
            reasons.append("dynamic_driver_missing")
        if not driver.get("matched_control"):
            reasons.append("matched_dynamic_control_missing")

    claim_class = receipt.get("claim_class")
    firewall = receipt.get("analogy_firewall", {})
    if claim_class in {"MATHEMATICAL_CORRESPONDENCE", "PHYSICAL_MECHANISM"}:
        if firewall.get("mapping_defined") is not True:
            reasons.append("cross_domain_mapping_not_defined")
        if firewall.get("prediction_defined") is not True:
            reasons.append("discriminating_prediction_not_defined")
    if claim_class == "PHYSICAL_MECHANISM" and firewall.get("mechanism_evidence") is not True:
        reasons.append("physical_mechanism_evidence_missing")

    return reasons


def evaluate(receipt: Dict[str, Any]) -> Dict[str, Any]:
    errors = validate(receipt)
    reasons: List[str] = []

    if errors:
        return {"decision": "REJECT", "reasons": errors}

    if receipt["license_state"] in {"unknown", "restricted"}:
        reasons.append("license_not_cleared_for_code_ingestion")

    benchmark_ok = metric_pass(receipt["benchmark"])
    invariance_ok = metric_pass(receipt["invariance"])
    controls_ok = metric_pass(receipt["controls"])
    replay_ok = metric_pass(receipt["replay"])

    if not benchmark_ok:
        reasons.append("known_answer_calibration_failed")
    if not invariance_ok:
        reasons.append("transformation_invariance_failed")
    if not controls_ok:
        reasons.append("control_separation_failed")
    if not replay_ok:
        reasons.append("replay_failed")

    reasons.extend(module_gates(receipt))

    hard_fail = any(reason for reason in reasons if reason not in {
        "license_not_cleared_for_code_ingestion", "independent_reproduction_pending"
    })

    if hard_fail:
        decision = "REJECT"
    elif receipt["license_state"] in {"unknown", "restricted"}:
        decision = "EXPERIMENTAL"
    elif receipt["claim_class"] in {"ANALOGY", "HYPOTHESIS", "SPECULATION"}:
        decision = "EXPERIMENTAL"
        reasons.append("claim_class_not_promotable_to_mechanism")
    elif receipt.get("formal_proof", {}).get("verified") is True:
        decision = "PROOF_BACKED"
    elif receipt.get("independent_reproduction", {}).get("pass") is True:
        decision = "VALIDATED_COMPONENT"
    else:
        decision = "EXPERIMENTAL"
        reasons.append("independent_reproduction_pending")

    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    return {
        "decision": decision,
        "reasons": sorted(set(reasons)),
        "receipt_sha256": hashlib.sha256(canonical).hexdigest(),
        "component_id": receipt["component_id"],
        "revision": receipt["revision"],
        "cp8_stage": receipt["cp8_stage"],
        "claim_class": receipt["claim_class"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a CP8 component receipt")
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--verify-input", type=Path)
    args = parser.parse_args()

    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    if args.verify_input:
        actual = sha256_file(args.verify_input)
        expected = receipt.get("input_sha256")
        if actual != expected:
            print(json.dumps({
                "decision": "REJECT",
                "reasons": ["input_hash_mismatch"],
                "expected": expected,
                "actual": actual,
            }, indent=2, sort_keys=True))
            return 2

    result = evaluate(receipt)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] != "REJECT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
