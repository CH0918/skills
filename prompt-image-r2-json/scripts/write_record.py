#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Write prompt image metadata JSON.")
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--image-url", action="append", required=True)
    parser.add_argument("--category", action="append", default=[])
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--aspect-ratio", required=True)
    parser.add_argument("--sort-order", type=int, default=1)
    parser.add_argument("--author-name", default="")
    parser.add_argument("--author-link", default="")
    parser.add_argument("--source-link", default="")
    args = parser.parse_args()

    record = {
        "title": args.title,
        "prompt": args.prompt,
        "description": args.description,
        "imageUrls": args.image_url,
        "categories": args.category,
        "tags": args.tag,
        "aspectRatio": args.aspect_ratio,
        "sortOrder": args.sort_order,
        "language": "en",
        "authorName": args.author_name,
        "authorLink": args.author_link,
        "sourceLink": args.source_link,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([record], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    json.loads(out.read_text(encoding="utf-8"))
    print(out)


if __name__ == "__main__":
    main()
