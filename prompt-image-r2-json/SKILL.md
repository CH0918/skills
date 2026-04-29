---
name: prompt-image-r2-json
description: Generate or edit an image from a Chinese user prompt, lightly polish and translate the prompt into English, save the generated image into the current project, upload it to Cloudflare R2 with Wrangler, and write an import-ready English JSON record. Use when the user asks to turn Chinese image prompts into generated assets, R2 image URLs, or database-ready JSON for prompt/image collections.
---

# Prompt Image R2 JSON

## Overview

Use this skill to turn a Chinese image prompt into a reusable image record:

1. Polish the Chinese prompt lightly without changing the intent.
2. Translate and normalize it into a production-grade English image prompt.
3. Generate the image, then copy the final image into the current project.
4. Upload the image to Cloudflare R2 with Wrangler.
5. Write a JSON file whose user-facing fields are in English.

Default public image domain: `https://img.img2ai.org`.

Default R2 bucket: infer from local context when possible; if there is evidence of `img2ai`, use `img2ai`.

## Workflow

1. Inspect the current project for existing conventions:
   - output directories such as `images/`, `assets/`, `output/`, `data/`
   - existing JSON shape
   - Wrangler or R2 hints, including `.wrangler/state/v3/r2`, `wrangler.toml`, and previous files
2. Convert the Chinese prompt:
   - preserve all concrete constraints
   - translate all final JSON values into English
   - if the prompt mentions a user-uploaded reference image but none is available, state the limitation and use a reasonable generated subject if the user allows it
3. Generate the image with the `imagegen` skill or built-in `image_gen` tool.
4. Copy the selected generated image from `$CODEX_HOME/generated_images/...` into the project, usually `images/<slug>.png`.
5. Upload to R2:
   - run `wrangler r2 object put <bucket>/<key> --file <local-image> --content-type image/png --remote`
   - use `--remote`; without it, Wrangler may write only to local Miniflare R2 state
   - choose a stable key such as `prompt-collect/<slug>.png`
6. Build the public image URL:
   - `https://img.img2ai.org/<key>`
   - do not use `r2://...` in `imageUrls` unless the user explicitly asks for internal R2 paths
7. Write JSON to the project, usually `output/<slug>.json`.
8. Validate:
   - JSON parses
   - image file exists locally
   - optional remote check: `wrangler r2 object get <bucket>/<key> --remote --file /private/tmp/<slug>-check.png`

## JSON Shape

Write an array with exactly this shape unless the user provides a different schema:

```json
[
  {
    "title": "",
    "prompt": "",
    "description": "",
    "imageUrls": [],
    "categories": [],
    "tags": [],
    "aspectRatio": "",
    "sortOrder": 1,
    "language": "en",
    "authorName": "",
    "authorLink": "",
    "sourceLink": ""
  }
]
```

Field rules:

- `title`: concise English title, Title Case.
- `prompt`: polished English generation prompt used for the image.
- `description`: English description of the final image and use case.
- `imageUrls`: public URLs under `https://img.img2ai.org/<key>`.
- `categories`: 2-5 broad English category names.
- `tags`: 6-12 specific English tags.
- `aspectRatio`: requested ratio, such as `4:3`, `1:1`, `16:9`, or `9:16`.
- Keep `language` as `en`.
- Leave `authorName`, `authorLink`, and `sourceLink` empty unless the user provides them.

## Helper Script

Use `scripts/write_record.py` to write and validate the JSON when helpful. It accepts the final metadata as CLI flags and writes the schema above.

Example:

```bash
python /Users/chdj/.codex/skills/prompt-image-r2-json/scripts/write_record.py \
  --out output/example.json \
  --title "AI Summer Office Shoes Styling and Proportion Report" \
  --prompt "Create a high-fidelity horizontal 4:3 editorial infographic..." \
  --description "A premium AI image-consultant report..." \
  --image-url "https://img.img2ai.org/prompt-collect/example.png" \
  --category "Fashion Styling" \
  --category "Infographic" \
  --tag "summer office shoes" \
  --tag "commute styling" \
  --aspect-ratio "4:3"
```

## Naming

Use stable, lowercase slugs:

- derive from the English title
- replace non-alphanumeric runs with hyphens
- trim leading/trailing hyphens
- keep under 80 characters

Typical paths:

- local image: `images/<slug>.png`
- R2 key: `prompt-collect/<slug>.png`
- JSON: `output/<slug>.json`

## Response

In the final answer, report only the useful artifacts:

- local image path
- public image URL
- JSON file path
- whether remote R2 upload was verified
