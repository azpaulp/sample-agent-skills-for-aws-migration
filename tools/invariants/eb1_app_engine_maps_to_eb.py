#!/usr/bin/env python3
"""EB1: App Engine maps to Elastic Beanstalk in Design output.

Invariant
---------
When google_app_engine_application is present in the inventory AND the user
has NOT explicitly overridden with compute_model "container_orchestration"
or "serverless", it must map to "Elastic Beanstalk" in aws-design.json.

If compute_model is "container_orchestration" or "serverless", App Engine
may map to Fargate or Lambda instead — this is valid and passes.

Skill file reference
--------------------
  fast-path.md (Direct Mappings table)
    google_app_engine_application → Elastic Beanstalk
    Condition: compute_model absent or "managed_platform"

  design-refs/compute.md (App Engine subsection)
    Default → Elastic Beanstalk (PaaS-to-PaaS)
    User prefers container control → Fargate
    Event-driven / scale-to-zero → Lambda

Examples
--------
  PASS: App Engine maps to "Elastic Beanstalk" with default preferences.
  PASS: App Engine maps to "Fargate" with compute_model: "container_orchestration".
  FAIL: App Engine maps to "Fargate" with compute_model absent or "managed_platform".
"""

import json
import sys
from pathlib import Path


def main():
    migration_dir = Path(sys.argv[1])
    design_file = migration_dir / "aws-design.json"
    prefs_file = migration_dir / "preferences.json"

    if not design_file.exists():
        print(json.dumps({"status": "fail", "details": "aws-design.json not found"}))
        return

    compute_model = None
    if prefs_file.exists():
        prefs = json.loads(prefs_file.read_text(encoding="utf-8"))
        compute_model = (
            prefs.get("design_constraints", {})
            .get("compute_model", {})
            .get("value")
        )

    user_overrode = compute_model in ("container_orchestration", "serverless")

    data = json.loads(design_file.read_text(encoding="utf-8"))
    found_app_engine = False
    violations = []

    for cluster in data.get("clusters", []):
        for resource in cluster.get("resources", []):
            gcp_type = resource.get("gcp_type", "")
            if "app_engine_application" in gcp_type:
                found_app_engine = True
                aws_service = resource.get("aws_service", "").lower()

                if user_overrode:
                    if "beanstalk" in aws_service:
                        violations.append(
                            f"{resource.get('gcp_address')}: mapped to EB but "
                            f"compute_model is '{compute_model}' (should be Fargate/Lambda)"
                        )
                else:
                    if "beanstalk" not in aws_service:
                        violations.append(
                            f"{resource.get('gcp_address')}: mapped to "
                            f"'{resource.get('aws_service')}' instead of Elastic Beanstalk"
                        )

    if not found_app_engine:
        print(json.dumps({"status": "fail", "details": "No App Engine resource found in design"}))
    elif violations:
        print(json.dumps({"status": "fail", "details": "; ".join(violations[:5])}))
    else:
        print(json.dumps({"status": "pass"}))


if __name__ == "__main__":
    main()
