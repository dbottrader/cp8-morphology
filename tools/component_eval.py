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
    "component_id",
    "revision",
    "source",
    "license_state",
    "cp8_stage",
    "input_sha256",
    "output_sha256",
    "benchmark",
    "invariance",
    "controls",
    "replay",
]


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
        "permissive",
        "compatible",
        "unknown",
        "restricted",
        "internal",
    }:
        errors.append("invalid:license_state")

    for section in ("benchmark", "invariance", "controls", "replay"):
        if section in receipt and not isinstance(receipt[section], dict):
            errors.append(f"invalid_section:{section}")
    return errors


def metric_pass(section: Dict[str, Any]) -> bool:
    """Require explicit pass=true; absence never implies success."""
    return section.get("pass") is True


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

    hard_fail = not all((benchmark_ok, invariance_ok, controls_ok, replay_ok))
    if hard_fail:
        decision = "REJECT"
    elif receipt["license_state"] in {"unknown", "restricted"}:
        decision = "EXPERIMENTAL"
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
        "reasons": reasons,
        "receipt_sha256": hashlib.sha256(canonical).hexdigest(),
        "component_id": receipt["component_id"],
        "revision": receipt["revision"],
        "cp8_stage": receipt["cp8_stage"],
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
