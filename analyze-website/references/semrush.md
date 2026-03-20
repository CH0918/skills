# Semrush Workflow

Use this reference only when the analysis needs current traffic, SEO, backlink, competitor, or AI visibility data.

## Entry point

Prefer the mirror provided in the environment when it is reachable:

- `https://sem.3ue.co/home/`

Search by root domain whenever the target is a company website. Use URL-level views only when you need to analyze a specific landing page or content page.

## Priority pages

Collect the smallest useful set first:

1. `analytics/overview`
2. `analytics/organic/overview`
3. `analytics/backlinks/overview`
4. `ai-seo/overview`

Open extra pages only if the user asks for more depth:

- `analytics/toppages`
- `analytics/comparedomains`
- `analytics/keywordgap`
- `analytics/refdomains/report`
- `analytics/traffic/traffic-overview`

## What to collect

### Domain overview

Use for high-level acquisition and moat signals:

- Authority Score
- organic traffic
- paid traffic
- referring domains
- organic keywords
- paid keywords
- report date
- selected market/database
- selected device if visible

### Organic overview

Use for SEO-led acquisition analysis:

- market/database being viewed
- report month or date
- leading topic clusters
- traffic direction
- high-level keyword distribution if visible

Do not copy long keyword tables into the report. Summarize patterns.

### Backlinks overview

Use for defensibility and acquisition quality:

- referring domains
- total backlinks
- monthly visits shown on the page if available
- backlink growth or decline
- top referring domain categories
- top anchor patterns
- competitor domains shown in backlink similarity widgets

### AI visibility overview

Use only when the product has meaningful AI-search exposure or the user explicitly cares about AI distribution:

- AI visibility score
- mentions
- citations
- cited pages
- country mix
- LLM/platform mix
- visible “data as of” date

Treat this as directional third-party data, not official company demand.

## Citation discipline

When citing Semrush-derived numbers, include:

- the page type, such as `Semrush domain overview`
- the visible date from the UI
- the market/database, such as `Worldwide` or `US`
- the scope if relevant, such as `Desktop`

Good example:

- `Semrush domain overview for shutterstock.com, Worldwide, Desktop, report date 2026-03-19`

## Interpretation rules

- Use Domain Overview for directional scale, not accounting-grade precision.
- Do not mix `Worldwide` and `US` values in the same sentence without saying so.
- Backlink metrics, traffic metrics, and AI visibility metrics often use different scopes; preserve those scopes in the writeup.
- If Semrush shows values that materially differ from another tool, note the mismatch and keep going.
- If a Semrush widget looks obviously noisy or irrelevant to the business analysis, ignore it rather than forcing it into the report.

## Minimum Semrush bundle for a normal teardown

For most website analyses, the minimum useful set is:

- Domain Overview
- Backlinks Overview
- AI Visibility Overview if available

Add Organic Overview only when SEO is clearly a major growth lever or when the user asks how the site gets traffic.
