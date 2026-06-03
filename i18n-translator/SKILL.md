---
name: i18n-translator
description: Synchronize JSON locale files from a base language file, usually en.json. Use when Codex needs to create target locale JSON files, detect and translate missing i18n keys, incrementally update existing translations, preserve existing translated values, or migrate the Flat Copilot VSCode i18n translator workflow into a reusable skill.
---

# I18n Translator

## Core Workflow

Use this skill for JSON-based i18n folders where one base file is the source of truth and target files are named by language code, such as `en.json`, `zh.json`, `ja.json`, or `fr.json`.

Default to `en.json` as the base file. Preserve existing target translations. Only add keys that exist in the base file and are missing, empty, or non-string in a target file.

1. Locate the locale directory and confirm it contains the base JSON file.
2. Prefer `scripts/sync_i18n.py translate <locale-dir>` for normal work; it analyzes missing keys, batch-translates them, and applies the result.
3. Use the manual `analyze` -> translate -> `apply` path only when the user wants to inspect or edit the translation mapping before writing files.
4. Review the diff and, for code projects, run the repository's normal lint or JSON validation command.

## Script Usage

Analyze existing locale files:

```bash
python <skill-dir>/scripts/sync_i18n.py analyze path/to/locales --base en.json --output /tmp/i18n-missing.json
```

Analyze specific targets, including files that do not exist yet:

```bash
python <skill-dir>/scripts/sync_i18n.py analyze path/to/locales --targets zh,ja,fr --output /tmp/i18n-missing.json
```

Apply translations:

```bash
python <skill-dir>/scripts/sync_i18n.py apply path/to/locales /tmp/i18n-translations.json
```

Batch translate and apply in one command:

```bash
python <skill-dir>/scripts/sync_i18n.py translate path/to/locales \
  --targets zh,ja,fr \
  --batch-size 50 \
  --delay-between-batches 1500 \
  --max-concurrency 6 \
  --concurrency-threshold 10
```

Test the configured Anthropic-compatible API before a large translation run:

```bash
python <skill-dir>/scripts/sync_i18n.py test-api
```

## Configuration

Create a local config file before using `translate` or `test-api`:

```bash
cp <skill-dir>/config.example.json <skill-dir>/config.json
```

Then edit `config.json`:

```json
{
  "authToken": "your-api-key",
  "baseUrl": "http://8.134.145.9:8080",
  "model": "gemini-2.5-flash[1m]",
  "timeout": 300,
  "maxTokens": 4096,
  "temperature": 0,
  "batch": {
    "batchSize": 50,
    "delayBetweenBatches": 1500,
    "maxConcurrency": 6,
    "concurrencyThreshold": 10,
    "maxPromptKb": 128,
    "retries": 1,
    "retryDelay": 1500
  }
}
```

`config.json` is ignored by git. Do not commit real API keys.

Config lookup order:

1. `--config /path/to/config.json`
2. `I18N_TRANSLATOR_CONFIG=/path/to/config.json`
3. `<skill-dir>/config.json`
4. `~/.codex/i18n-translator/config.json`

Runtime value priority:

1. Explicit CLI flags such as `--model` or `--batch-size`
2. Environment variables such as `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`
3. Config file values
4. Script defaults

The apply command accepts either format:

```json
{
  "translations": [
    { "language": "zh", "key": "common.save", "text": "保存" }
  ]
}
```

```json
{
  "zh": {
    "common.save": "保存"
  }
}
```

## Translation Rules

Translate UI text naturally and concisely. Keep placeholders, interpolation tokens, HTML-like tags, variables, punctuation style, and newline structure intact.

Do not translate keys. Do not rewrite existing target values unless the user explicitly asks for a full refresh or correction pass.

For arrays, treat numeric path segments as array indices. For nested objects, preserve the base structure when inserting missing values.

## Batch Translation Strategy

Keep the Flat Copilot plugin's tuned batch behavior:

- Default `batch-size`: `50`
- Default `delay-between-batches`: `1500` ms
- Default `max-concurrency`: `6`
- Default `concurrency-threshold`: `10`
- If task count is below the threshold, use serial batches.
- If task count reaches the threshold, use fixed max concurrency and dynamic batch size: `ceil(totalTasks / concurrency)`, capped by `batch-size`.
- Process concurrent batches in rounds. Between rounds, wait half the configured delay, with a minimum of `500` ms.
- Keep a `128KB` max prompt guard per batch, matching the original plugin's prompt-size protection.
- Do not create `.bak` files by default. Add `--backup` only when the user explicitly asks to keep file backups.

The script calls an Anthropic-compatible relay. Read the API key from config or `ANTHROPIC_AUTH_TOKEN`; never hard-code it in committed files. Configure `baseUrl` and `model` in `config.json` when the relay or model changes. Default base URL is `http://8.134.145.9:8080`; default model is `gemini-2.5-flash[1m]`.

## Language Reference

For the Flat Copilot preset language list and language-code conventions, read `references/languages.md` only when target language selection is needed.
