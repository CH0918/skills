---
name: collect-playground-data
description: Create SEO-ready Img2AI image playground backend JSON from social media prompts, reference images, generated sample images, or mixed prompt/image batches. Use when the user asks to collect playground data, turn prompts into image_playground_case JSON, upload attached images to R1/R2/storage, generate missing sample images before upload, or prepare SEO title/description/H1/FAQ content for playground pages.
---

# Collect Playground Data

## Workflow

1. Gather each source item: original prompt, source notes, intended style/use case, optional attached/reference image, and desired route path if provided.
2. Prepare an input/reference image for every case. If the user attaches or provides an input image, use that image. If no input image is provided, generate one first:
   - For prompts about people, generate a clean reference model/person image that matches the subject needed by the prompt.
   - For prompts not about people, generate a clean reference object/product/scene image that matches the subject needed by the prompt.
3. Generate the output/result image from the input image plus the collected prompt. Use image editing/reference mode so the output demonstrates the prompt against the prepared input.
4. Upload both input and output images to the project's R1/R2 storage and use the returned/public URLs in the JSON.
5. Write one JSON object per playground case using `image_playground_case` fields.
6. Run `scripts/validate_playground_json.py` on the output before delivering it.

For the exact schema and copy rules, read `references/schema.md`.

## Project Output Directory

- For `/Users/chdj/project/site-projects/img2ai`, save generated playground JSON files under `/Users/chdj/project/site-projects/img2ai/proground-data/` by default.
- Use descriptive lowercase filenames such as `male-fashion-infographic-playground.json`.
- Validate the file from its final project path before delivering it.

## Image Handling

- Treat user-attached images as `inputImageUrl` unless the user explicitly says they are generated results.
- If no input/reference image is supplied, call the `image-generator` skill to create one:
  - Use a neutral, reusable reference image prompt, not the final transformation prompt.
  - Prefer an input image that looks like a plausible real user upload, not an already-polished final result. The before/after contrast should be obvious enough to make users want to try the tool.
  - If the final prompt targets a person, generate a suitable lifestyle, selfie, casual portrait, or everyday photo as the reference image when appropriate. Avoid making the input look like a studio headshot, poster, ad, or finished profile image unless that is the actual source use case.
  - If the final prompt targets an object, product, animal, room, landscape, or graphic, generate a natural source-style image for that subject instead of a fully optimized final image. For example, use a simple product photo, messy room photo, casual pet snapshot, or ordinary landscape photo when the result is meant to upgrade or stylize it.
  - Avoid copyrighted characters, brand logos, celebrity likenesses, protected likenesses, or trademarked worlds unless the user explicitly has rights and asks for them.
- Generate the final `outputImageUrl` image by calling the `image-generator` skill again with the prepared input image as `--ref` and the user-provided transformation prompt as the generation/edit prompt.
- When generating the output image, emphasize a clear transformation from the input image to the desired result. The output should visibly improve or change composition, styling, lighting, background, wardrobe, layout, polish, or presentation while preserving the requested subject identity/details.
- For playground examples, the input and output images should create a strong visual before/after pair. Avoid pairs where the input is already too close to the output, because weak contrast reduces perceived value and user motivation.
- Save generated local images in the project output directory or a subdirectory under it, using clear names such as `<slug>-input.png` and `<slug>-output.png`.
- Upload both images with Wrangler to Cloudflare storage:
  - Bucket: `img2ai`
  - Public domain: `https://img.img2ai.org`
  - Upload path prefix: `prompt-collect`
  - Object key pattern: `prompt-collect/<slug>-input.<ext>` and `prompt-collect/<slug>-output.<ext>`.
- Use Wrangler R2 object upload, for example:

```bash
pnpm exec wrangler r2 object put img2ai/prompt-collect/example-input.png --file /absolute/path/example-input.png
pnpm exec wrangler r2 object put img2ai/prompt-collect/example-output.png --file /absolute/path/example-output.png
```

- After upload, set URLs as `https://img.img2ai.org/prompt-collect/<filename>`.
- If Wrangler authentication or network access is unavailable, keep the generated local image paths, explain the upload blocker, and do not invent public URLs.

## Copy Rules

- Produce strong SEO copy, not literal social-media captions.
- Keep TDH concise:
  - `title`: about 45-60 characters when practical.
  - `description`: about 120-155 characters when practical.
  - `h1`: direct and readable, usually under 70 characters.
  - `nav_name`: short navigation label, usually 2-5 words in English or 4-10 Chinese characters.
- Include the primary keyword naturally near the front, usually based on the route/use case.
- Keep prompts detailed enough to reproduce the visual style, composition, lighting, subject, constraints, and output format.
- When a prompt targets a person and the source text explicitly specifies gender, remove the gender-specific wording unless gender is the actual product/use-case requirement. Make collected prompts reusable for any uploaded person photo, so users can provide either male or female subjects.
- Write `en` and `zh` by default for Img2AI admin-ready data. If the user explicitly asks for English-only output, omit `zh`. Localize naturally instead of translating word-for-word.
- FAQ should answer search intent and product-use questions. Use 3-5 concise items unless the user asks for more.

## Output Contract

Return valid JSON only when the user asks for importable data. Use an array for multiple cases:

```json
[
  {
    "path": "ai-headshot-generator",
    "inputImageUrl": "https://...",
    "outputImageUrl": "https://...",
    "translations": {
      "en": {
        "title": "AI Headshot Generator from Photo | Img2AI",
        "description": "Create polished AI headshots from a reference photo with a detailed prompt for lighting, wardrobe, background, and expression.",
        "h1": "AI Headshot Generator from Photo",
        "nav_name": "AI Headshot",
        "prompt": "A detailed generation prompt...",
        "faq": [
          {
            "question": "Can I use a selfie as the reference photo?",
            "answer": "Yes. Upload a clear selfie and describe the headshot style, background, lighting, and wardrobe you want."
          }
        ]
      },
      "zh": {
        "title": "AI 证件照生成器 | Img2AI",
        "description": "上传参考照片，用清晰提示词生成专业 AI 证件照，控制光线、服装、背景和表情。",
        "h1": "AI 证件照生成器",
        "nav_name": "AI 证件照",
        "prompt": "一段自然本地化后的中文提示词...",
        "faq": [
          {
            "question": "可以用自拍照作为参考图吗？",
            "answer": "可以。建议上传清晰、光线充足的自拍照，并在提示词里说明背景、服装、光线和表情。"
          }
        ]
      }
    },
    "status": "published",
    "sortOrder": 10
  }
]
```

Do not include database-managed fields such as `id`, `createdAt`, or `updatedAt` unless the user explicitly asks for a full row export.

## Validation

Save the draft JSON to the project output directory when working in `/Users/chdj/project/site-projects/img2ai`, then run validation on that final file path. For example:

```bash
python /Users/chdj/.codex/skills/collect-playground-data/scripts/validate_playground_json.py /Users/chdj/project/site-projects/img2ai/proground-data/example-playground.json
```

Fix every reported issue before final delivery.
