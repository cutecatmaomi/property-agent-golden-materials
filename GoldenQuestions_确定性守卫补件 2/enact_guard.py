"""Enact ingress adapter for the original Golden Questions response policy."""

import json
import sys

from response_policy import classify_message, fixed_reply


def guard_message(message: str, *, estate_id: str) -> dict:
    """Run after authentication and input validation, before the model."""
    reason = classify_message(message)
    if reason is None:
        return {"handled": False, "reply": None}

    result = fixed_reply(estate_id, reason)
    return {
        "handled": True,
        "reply": {
            "kind": result["response_type"],
            "text": result["message"],
            "data": result,
            "trace": ["guard", "render"],
        },
    }


def main() -> None:
    try:
        request = json.load(sys.stdin)
        if not isinstance(request, dict):
            raise ValueError
        message, estate_id = request["message"], request["estate_id"]
        if not isinstance(message, str) or not 1 <= len(message.strip()) <= 300:
            raise ValueError
        if not isinstance(estate_id, str) or not estate_id:
            raise ValueError
    except (ValueError, KeyError, TypeError):
        raise SystemExit("Expected a JSON object with message and authenticated estate_id") from None

    result = guard_message(message.strip(), estate_id=estate_id)
    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
