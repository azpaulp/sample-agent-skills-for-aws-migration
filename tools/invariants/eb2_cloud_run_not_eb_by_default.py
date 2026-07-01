#!/usr/bin/env python3
"""EB2: Cloud Run must NEVER map to Elastic Beanstalk.

Invariant
---------
When google_cloud_run_service or google_cloud_run_v2_service is present,
it must NOT map to Elastic Beanstalk regardless of compute_model preference.
Cloud Run maps to Fargate unconditionally via fast-path ("Always").
The compute_model preference only affects App Engine resources.

Skill file reference
--------------------
  fast-path.md (Direct Mappings table)
    google_cloud_run_service → Fargate (Always)
    google_cloud_run_v2_service → Fargate (Always)

  design-refs/compute.md (Cloud Run section)
    "Cloud Run maps to Fargate via deterministic fast-path ('Always').
     The compute_model preference does not affect Cloud Run mapping."

Examples
--------
  PASS: Cloud Run maps to "Fargate" (any preference state).

  FAIL: Cloud Run maps to "Elastic Beanstalk" (any preference state).
"""

import json
import sys
from pathlib import Path


def main():
    migration_dir = Path(sys.argv[1])
    design_file = migration_dir / "aws-design.json"

    if not design_file.exists():
        print(json.dumps({"status": "fail", "details": "aws-design.json not found"}))
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
                        f"'{resource.get('aws_service')}' (must always be Fargate)"
                    )

    if violations:
        print(json.dumps({"status": "fail", "details": "; ".join(violations[:5])}))
    else:
        print(json.dumps({"status": "pass"}))


if __name__ == "__main__":
    main()
