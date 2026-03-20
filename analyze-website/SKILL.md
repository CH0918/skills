---
name: analyze-website
description: Analyze a website, product site, SaaS homepage, AI tool site, or competitor landing page with a fixed 14-dimension framework and produce a Markdown teardown. Use when the user asks to analyze a site from a business/product perspective, summarize how a website makes money, review acquisition channels, estimate revenue, compare positioning, or turn a one-off website analysis into a reusable report or workflow. Prefer this skill when current traffic, SEO, backlink, or AI visibility data should be verified from live sources such as Semrush before writing.
---

# Analyze Website

Use this skill to turn a website into a structured business and product analysis instead of an unstructured summary.

Prefer this workflow when the user gives a URL and wants a repeatable teardown, especially for SaaS, AI tools, ecommerce tools, marketplaces, or productized service sites.

## Workflow

### 1. Confirm scope and output

Determine:

- the target URL or product
- whether the user explicitly does not want a saved Markdown report
- whether the user wants the full 14 dimensions or a compressed version

Default behavior: always write the final analysis to a `.md` file in the current workspace unless the user explicitly asks for chat-only output.

Use the website domain as the filename stem whenever a URL is available.

Examples:

- `shutterstock.com` -> `shutterstock.com.md`
- `www.remove.bg` -> `remove.bg.md`
- `openai.com` -> `openai.com.md`

If the request is about a product rather than a URL, use a clear normalized slug.

### 2. Gather first-party evidence

Open the target site with browser tooling first when available.

Collect:

- homepage positioning and hero copy
- navigation structure
- audience segmentation pages
- pricing and plan structure
- integrations, API, enterprise, case study, about, help, and blog pages

Use the product's own pages as the primary source for:

- product scope
- intended users
- packaging and pricing
- workflow integrations
- customer logos and testimonials
- scale claims such as monthly users or processed volume

### 3. Gather third-party evidence

Use current public sources for anything temporally unstable or not explicitly on the site:

- traffic and channel mix
- third-party reviews and ratings
- app marketplace sentiment
- company, acquisition, or ownership changes
- market context and competitor references

Prefer official sources first, then reputable third-party aggregators. Include exact dates when citing current metrics.

Read [references/evidence.md](references/evidence.md) for source priority and estimation guardrails.

If browser tooling can access the Semrush mirror at `https://sem.3ue.co/`, use it as the default traffic and SEO source before falling back to search snippets or other third-party aggregators. Read [references/semrush.md](references/semrush.md) only when you need traffic, keyword, backlink, or AI visibility metrics.

### 4. Separate facts from inference

Keep these distinct:

- `Official facts`: directly supported by the company site or official docs
- `Third-party facts`: traffic, ratings, or current market data from external sources
- `Inference`: your synthesis, especially around moat, acquisition strategy, and likely revenue

Do not present traffic, conversion, or revenue estimates as if the company disclosed them.

### 5. Analyze with the 14-dimension framework

Use the fixed framework in [references/framework.md](references/framework.md).

Maintain the original intent of each dimension:

1. What problem does this product solve?
2. Who is the user?
3. Why do users need it?
4. How do users evaluate it?
5. How does it find users?
6. Does it make money? How much?
7. What did I learn from it?
8. What is hard to copy and why?
9. One-sentence pitch
10. If I built the same thing, what would I do differently?
11. Can I build it? What resources are required?
12. How would I find users?
13. Why me? What unique fit would I need?
14. Do I like this product?

Compress or expand sections based on the user's request, but preserve the same analytical spine.

### 6. Write the report

Default output is a Markdown report saved as a file in the workspace. Do not stop at an in-chat answer only unless the user explicitly opts out of file output.

The filename should use the analyzed website domain when possible:

- `domain.md`

Examples:

- `shutterstock.com.md`
- `figma.com.md`
- `notion.so.md`

The report should include:

- title
- analysis date
- target URL
- method note
- 14 sections
- short summary
- sources

Use concise business language. Avoid filler. Make it easy to scan.

After writing the file, also provide the result in chat with a short summary and mention the saved file path.

When Semrush data is used, include the visible report date and scope in the writeup where it matters, for example:

- database or market: `Worldwide`, `US`, `UK`
- device scope: `Desktop` or `Mobile` if shown
- report date: the exact date shown in the UI
- metric source page: domain overview, organic overview, backlinks overview, AI visibility, or traffic overview

## Output rules

- Use exact dates for traffic, pricing, reviews, and ownership facts when available.
- Quote only short snippets when necessary; otherwise paraphrase.
- Include source links at the end.
- Call out uncertainty explicitly.
- If a section cannot be verified, say so briefly and move on instead of fabricating.
- If Semrush and another third-party tool disagree, prefer the source that is more direct for that metric and mention the mismatch briefly instead of smoothing it over.

## Adaptation rules

- If the target is mostly a marketing site, lean harder on positioning, acquisition, pricing, and social proof.
- If the target is developer tooling, lean harder on docs, API, integrations, open source/community, and pricing mechanics.
- If the target is ecommerce or marketplace infrastructure, lean harder on workflow, merchant value, catalog operations, and channel strategy.
- If the target is early-stage or has limited public data, shorten the revenue and traffic confidence, and increase caveats.

## References

- For the full 14-dimension checklist and report skeleton, read [references/framework.md](references/framework.md).
- For evidence collection rules and estimation discipline, read [references/evidence.md](references/evidence.md).
- For Semrush collection paths, priority metrics, and citation rules, read [references/semrush.md](references/semrush.md).
