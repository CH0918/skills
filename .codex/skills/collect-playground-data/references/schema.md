# Img2AI Playground JSON Schema

Use this reference when creating backend data for the `image_playground_case` table.

## Table Fields

`image_playground_case` stores:

- `path`: required, unique route path without leading slash. Lowercase letters, digits, `/`, and `-`. Examples: `ai-headshot-generator`, `ghibli-style-portrait`.
- `inputImageUrl`: optional public URL for the reference/source image.
- `outputImageUrl`: optional public URL for the generated/result image.
- `translations`: required object keyed by locale.
- `status`: `published`, `draft`, or `archived`; default to `published`.
- `sortOrder`: optional positive integer.

Although `inputImageUrl` and `outputImageUrl` are schema-optional, the collection workflow should normally populate both. If no user input image is supplied, generate an input/reference image first, then generate the output image from that input plus the prompt, upload both images to `https://img.img2ai.org/prompt-collect/`, and store those public URLs.

Do not emit `id`, `createdAt`, or `updatedAt` for new-import JSON unless requested.

## Translation Shape

Each locale under `translations` may contain:

```json
{
  "title": "Short SEO title",
  "description": "Concise SEO meta description",
  "h1": "Readable page heading",
  "nav_name": "Short navigation label",
  "prompt": "The actual image generation prompt",
  "faq": [
    {
      "question": "Question?",
      "answer": "Answer."
    }
  ]
}
```

Required for admin import/use:

- `translations.en.title`
- `translations.en.h1`
- `translations.en.nav_name`
- `translations.en.prompt`

The current admin form expects `zh` fields when adding manually. Default to both `en` and `zh` for Img2AI admin-ready data unless the user explicitly requests English-only output.

## SEO Copy

- `title`: concise, keyword-led, usually 45-60 characters. Include `Img2AI` when it fits naturally.
- `description`: 120-155 characters when practical. Describe the action and value, not a generic slogan.
- `h1`: human-readable page title. Avoid stuffing multiple keywords.
- `nav_name`: compact label for navigation/sidebar use, shorter than `h1` and localized naturally.
- `faq`: answer real search questions: inputs, workflow, quality tips, usage rights, and how to edit prompts.

## Prompt Rewriting

When source prompts are copied from social media:

- Preserve the useful visual intent.
- Remove platform-specific filler, hashtags, engagement bait, and unrelated instructions.
- Make the prompt explicit about subject, style, camera/composition, lighting, background, color, texture, mood, and constraints.
- For prompts about a person, make the prompt gender-neutral by default. If the source prompt clearly says male/man/boy/he/him/his, female/woman/girl/she/her/hers, or equivalent gendered wording, remove or rewrite those parts so the prompt works with any uploaded person photo.
- Preserve gender only when it is the core use case or the user explicitly asks for a gender-specific page. Otherwise use neutral subject wording such as "the person", "the subject", "their", "portrait", or "uploaded photo".
- Avoid exact artist names, copyrighted characters, celebrity likenesses, brand logos, and trademarked worlds unless the user explicitly has rights and requests them.

## Example

```json
{
  "path": "watercolor-pet-portrait",
  "inputImageUrl": "https://img.img2ai.org/uploads/prompts/example-input.png",
  "outputImageUrl": "https://img.img2ai.org/uploads/prompts/example-output.png",
  "translations": {
    "en": {
      "title": "Watercolor Pet Portrait Generator | Img2AI",
      "description": "Turn a pet photo into a soft watercolor portrait with a detailed prompt for paper texture, gentle color, and expressive detail.",
      "h1": "Watercolor Pet Portrait Generator",
      "nav_name": "Pet Watercolor",
      "prompt": "Transform the uploaded pet photo into a delicate watercolor portrait on textured cold-press paper. Preserve the pet's face shape, markings, and expression while using soft layered washes, gentle edge bleeding, warm natural light, a clean cream background, and subtle hand-painted details. Keep the composition centered and avoid text, frames, collars with readable tags, or extra animals.",
      "faq": [
        {
          "question": "What kind of pet photo works best?",
          "answer": "Use a clear front-facing or three-quarter photo with good lighting so the model can preserve markings, expression, and face shape."
        },
        {
          "question": "Can I change the background style?",
          "answer": "Yes. Edit the prompt to request a plain paper background, floral wash, studio backdrop, or another watercolor setting."
        }
      ]
    }
  },
  "status": "published",
  "sortOrder": 10
}
```
