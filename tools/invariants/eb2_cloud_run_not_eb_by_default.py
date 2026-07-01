#!/usr/bin/env python3
"""EB2: Cloud Run without managed_platform preference does NOT map to EB.

Invariant
---------
When google_cloud_run_service or google_cloud_run_v2_service is present
and the user has NOT explicitly set compute_model to "managed_platform",
the resource must NOT map to Elastic Beanstalk. Cloud Run's default
target remains Fargate (per fast-path.md Direct Mappings).

Skill file reference
--------------------
  fast-path.md (Direct Mappings table)
    google_cloud_run_service → Fargate (Always)
    google_cloud_run_v2_service → Fargate (Always)

  design-refs/compute.md (Signals)
    Managed platform preference (compute_model: "managed_platform") →
    Elastic Beanstalk. Without this preference, Cloud Run stays on Fargate.

Examples
--------
  PASS: Cloud Run maps to "Fargate" with no managed_platform preference.

  FAIL: Cloud Run maps to "Elastic Beanstalk" without the user having
        explicitly requested a managed platform.
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

    has_managed_platform_pref = False
    if prefs_file.exists():
        prefs = json.loads(prefs_file.read_text(encoding="utf-8"))
        compute_model = (
            prefs.get("design_constraints", {})
            .get("compute_model", {})
            .get("value", "")
        )
        if compute_model == "managed_platform":
            has_managed_platform_pref = True

    if has_managed_platform_pref:
        print(json.dumps({"status": "pass", "details": "User chose managed_platform; EB is valid"}))
        return

    data = json.loads(design_file.read_text(encoding="utf-8"))
    violations = []

    for cluster in data.get("clusters", []):
        for resource in cluster.get("resources", []):
            gcp_type = resource.get("gcp_type", "")
            if "cloud_run" in gcp_type:
                aws_service = resource.get("aws_service", "").lower()
                if "beanstalk" in aws_service:
                    violations.append(
                        f"{resource.get('gcp_address')}: Cloud Run mapped to "
                        f"'{resource.get('aws_service')}' without managed_platform preference"
                    )

    if violations:
        print(json.dumps({"status": "fail", "details": "; ".join(violations[:5])}))
    else:
        print(json.dumps({"status": "pass"}))


if __name__ == "__main__":
    main()
