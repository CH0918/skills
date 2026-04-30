#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

PATH_RE = re.compile(r"^[a-z0-9](?:[a-z0-9/-]*[a-z0-9])?$")
STATUSES = {"published", "draft", "archived"}


def as_items(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    raise ValueError("top-level JSON must be an object or array")


def require(condition, message, errors):
    if not condition:
        errors.append(message)


def validate_translation(case_index, locale, value, errors):
    prefix = f"[{case_index}].translations.{locale}"
    require(isinstance(value, dict), f"{prefix} must be an object", errors)
    if not isinstance(value, dict):
        return

    for key in ("title", "h1", "nav_name", "prompt"):
        require(
            isinstance(value.get(key), str) and value[key].strip(),
            f"{prefix}.{key} is required",
            errors,
        )

    if "description" in value:
        require(
            isinstance(value["description"], str),
            f"{prefix}.description must be a string",
            errors,
        )

    faq = value.get("faq", [])
    require(isinstance(faq, list), f"{prefix}.faq must be an array", errors)
    if isinstance(faq, list):
        for faq_index, item in enumerate(faq):
            item_prefix = f"{prefix}.faq[{faq_index}]"
            require(isinstance(item, dict), f"{item_prefix} must be an object", errors)
            if isinstance(item, dict):
                require(
                    isinstance(item.get("question"), str) and item["question"].strip(),
                    f"{item_prefix}.question is required",
                    errors,
                )
                require(
                    isinstance(item.get("answer"), str) and item["answer"].strip(),
                    f"{item_prefix}.answer is required",
                    errors,
                )


def validate_case(index, item, errors):
    prefix = f"[{index}]"
    require(isinstance(item, dict), f"{prefix} must be an object", errors)
    if not isinstance(item, dict):
        return

    path = item.get("path")
    require(isinstance(path, str) and PATH_RE.match(path), f"{prefix}.path is invalid", errors)

    for key in ("inputImageUrl", "outputImageUrl"):
        if key in item and item[key] is not None:
            require(isinstance(item[key], str) and item[key].startswith("http"), f"{prefix}.{key} must be a public URL or null", errors)

    translations = item.get("translations")
    require(isinstance(translations, dict), f"{prefix}.translations must be an object", errors)
    if isinstance(translations, dict):
        require("en" in translations, f"{prefix}.translations.en is required", errors)
        for locale, value in translations.items():
            validate_translation(index, locale, value, errors)

    status = item.get("status", "published")
    require(status in STATUSES, f"{prefix}.status must be one of {sorted(STATUSES)}", errors)

    sort_order = item.get("sortOrder")
    if sort_order is not None:
        require(isinstance(sort_order, int) and sort_order >= 1, f"{prefix}.sortOrder must be a positive integer or null", errors)


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_playground_json.py <json-file>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        items = as_items(data)
    except Exception as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1

    errors = []
    for index, item in enumerate(items):
        validate_case(index, item, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: validated {len(items)} playground case(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
