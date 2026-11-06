"""Check the shipped guard against the original rules and reference cases."""

from pathlib import Path
import hashlib
import json
import subprocess
import sys

from enact_guard import guard_message
from response_policy import FIXED_SERVICE_REPLY, HUMAN_SERVICE_TERMS, RED_LINE_TERMS


def main() -> None:
    root = Path(__file__).resolve().parent
    cases = json.loads((root / "guard_cases.json").read_text(encoding="utf-8"))
    assert hashlib.sha256((root / "response_policy.py").read_bytes()).hexdigest() == cases["source_sha256"]
    assert (root / "FIXED_SERVICE_REPLY.txt").read_bytes() == FIXED_SERVICE_REPLY.encode("utf-8")
    assert len(RED_LINE_TERMS) == cases["red_line_terms_count"]
    assert len(HUMAN_SERVICE_TERMS) == cases["human_service_terms_count"]
    for row in cases["cases"]:
        result = guard_message(row["message"], estate_id=row["estate_id"])
        reason = row["expected_reason_code"]
        if reason is None:
            assert result == {"handled": False, "reply": None}, row["id"]
            continue
        assert result["handled"] is True, row["id"]
        assert result["reply"] == {
            "kind": "FIXED_REPLY",
            "text": FIXED_SERVICE_REPLY,
            "data": {
                "estate_id": row["estate_id"],
                "response_type": "FIXED_REPLY",
                "reason_code": reason,
                "red_line": reason == "RED_LINE",
                "message": FIXED_SERVICE_REPLY,
                "matches": [],
                "contact_channel": "PHONE",
                "contact_phone": "4001099888",
                "created": False,
            },
            "trace": ["guard", "render"],
        }, row["id"]
    for row in cases["cli_examples"]:
        request = {"message": row["message"], "estate_id": row["estate_id"]}
        check = subprocess.run(
            [sys.executable, "-B", str(root / "enact_guard.py")],
            input=json.dumps(request, ensure_ascii=False), text=True,
            capture_output=True, check=True,
        )
        assert json.loads(check.stdout) == guard_message(**request)
    print(f'{len(cases["cases"])} guard cases and {len(cases["cli_examples"])} CLI round-trips passed')


if __name__ == "__main__":
    main()
