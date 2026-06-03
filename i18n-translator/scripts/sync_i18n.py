#!/usr/bin/env python3
"""Analyze, batch-translate, and apply incremental JSON i18n translations."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


JsonObject = Dict[str, Any]
PathParts = List[str]

DEFAULT_MODEL = "gemini-2.5-flash[1m]"
DEFAULT_BASE_URL = "http://8.134.145.9:8080"
DEFAULT_TIMEOUT = 300
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0
DEFAULT_BATCH_SIZE = 50
DEFAULT_DELAY_BETWEEN_BATCHES = 1500
DEFAULT_MAX_CONCURRENCY = 6
DEFAULT_CONCURRENCY_THRESHOLD = 10
DEFAULT_MAX_PROMPT_KB = 128
DEFAULT_RETRIES = 1
DEFAULT_RETRY_DELAY = 1500
CONFIG_ENV_NAME = "I18N_TRANSLATOR_CONFIG"

LANG_NAMES: Dict[str, str] = {
    "ar": "阿拉伯语",
    "bn": "孟加拉语",
    "de": "德语",
    "es": "西班牙语",
    "fr": "法语",
    "hi": "印地语",
    "id": "印尼语",
    "it": "意大利语",
    "ja": "日语",
    "ms": "马来语",
    "pa": "旁遮普语",
    "pt": "葡萄牙语",
    "ru": "俄语",
    "ta": "泰米尔语",
    "te": "泰卢固语",
    "th": "泰语",
    "tr": "土耳其语",
    "ur": "乌尔都语",
    "vi": "越南语",
    "zh": "中文",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def skill_dir() -> Path:
    return script_dir().parent


def default_config_paths() -> List[Path]:
    return [
        skill_dir() / "config.json",
        Path.home() / ".codex" / "i18n-translator" / "config.json",
    ]


def load_config(path_value: str | None = None) -> JsonObject:
    candidates: List[Path] = []
    if path_value:
        candidates.append(Path(path_value).expanduser())
    elif os.environ.get(CONFIG_ENV_NAME):
        candidates.append(Path(os.environ[CONFIG_ENV_NAME]).expanduser())
    else:
        candidates.extend(default_config_paths())

    for path in candidates:
        if path.exists():
            data = load_json(path)
            if not isinstance(data, dict):
                raise ValueError(f"Config file must contain a JSON object: {path}")
            data["_configPath"] = str(path)
            return data
    return {}


def config_value(args: argparse.Namespace, config: JsonObject, attr: str, env_name: str, config_name: str, default: Any = None) -> Any:
    value = getattr(args, attr, None)
    if value is not None:
        return value
    if os.environ.get(env_name):
        return os.environ[env_name]
    return config.get(config_name, default)


def apply_runtime_config(args: argparse.Namespace) -> None:
    config = load_config(getattr(args, "config", None))
    args.config_data = config
    args.auth_token = config_value(args, config, "auth_token", "ANTHROPIC_AUTH_TOKEN", "authToken")
    args.base_url = config_value(args, config, "base_url", "ANTHROPIC_BASE_URL", "baseUrl", DEFAULT_BASE_URL)
    args.model = config_value(args, config, "model", "ANTHROPIC_MODEL", "model", DEFAULT_MODEL)
    args.timeout = int(config_value(args, config, "timeout", "I18N_TRANSLATOR_TIMEOUT", "timeout", DEFAULT_TIMEOUT))
    args.max_tokens = int(config_value(args, config, "max_tokens", "I18N_TRANSLATOR_MAX_TOKENS", "maxTokens", DEFAULT_MAX_TOKENS))
    args.temperature = float(config_value(args, config, "temperature", "I18N_TRANSLATOR_TEMPERATURE", "temperature", DEFAULT_TEMPERATURE))

    batch_config = config.get("batch") if isinstance(config.get("batch"), dict) else {}
    args.batch_size = int(config_value(args, batch_config, "batch_size", "I18N_TRANSLATOR_BATCH_SIZE", "batchSize", DEFAULT_BATCH_SIZE))
    args.delay_between_batches = int(
        config_value(args, batch_config, "delay_between_batches", "I18N_TRANSLATOR_DELAY_BETWEEN_BATCHES", "delayBetweenBatches", DEFAULT_DELAY_BETWEEN_BATCHES)
    )
    args.max_concurrency = int(config_value(args, batch_config, "max_concurrency", "I18N_TRANSLATOR_MAX_CONCURRENCY", "maxConcurrency", DEFAULT_MAX_CONCURRENCY))
    args.concurrency_threshold = int(
        config_value(args, batch_config, "concurrency_threshold", "I18N_TRANSLATOR_CONCURRENCY_THRESHOLD", "concurrencyThreshold", DEFAULT_CONCURRENCY_THRESHOLD)
    )
    args.max_prompt_kb = float(config_value(args, batch_config, "max_prompt_kb", "I18N_TRANSLATOR_MAX_PROMPT_KB", "maxPromptKb", DEFAULT_MAX_PROMPT_KB))
    args.retries = int(config_value(args, batch_config, "retries", "I18N_TRANSLATOR_RETRIES", "retries", DEFAULT_RETRIES))
    args.retry_delay = int(config_value(args, batch_config, "retry_delay", "I18N_TRANSLATOR_RETRY_DELAY", "retryDelay", DEFAULT_RETRY_DELAY))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def path_key(parts: PathParts) -> str:
    return ".".join(parts)


def is_int_segment(value: str) -> bool:
    return value.isdigit()


def extract_strings(value: Any, current: PathParts | None = None) -> List[Tuple[PathParts, str]]:
    current = current or []
    tasks: List[Tuple[PathParts, str]] = []

    if isinstance(value, dict):
        for key, child in value.items():
            tasks.extend(extract_strings(child, current + [str(key)]))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            tasks.extend(extract_strings(child, current + [str(index)]))
    elif isinstance(value, str) and value.strip():
        tasks.append((current, value))

    return tasks


def get_at_path(root: Any, parts: PathParts) -> Any:
    current = root
    for part in parts:
        if isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
        elif isinstance(current, list) and is_int_segment(part):
            index = int(part)
            if index >= len(current):
                return None
            current = current[index]
        else:
            return None
    return current


def set_at_path(root: Any, parts: PathParts, value: str) -> Any:
    if not parts:
        return value

    if root is None or not isinstance(root, (dict, list)):
        root = [] if is_int_segment(parts[0]) else {}

    current = root
    for index, part in enumerate(parts[:-1]):
        next_part = parts[index + 1]
        next_container: Any = [] if is_int_segment(next_part) else {}

        if isinstance(current, list):
            item_index = int(part)
            while len(current) <= item_index:
                current.append(None)
            if not isinstance(current[item_index], (dict, list)):
                current[item_index] = next_container
            current = current[item_index]
        else:
            if part not in current or not isinstance(current[part], (dict, list)):
                current[part] = next_container
            current = current[part]

    final = parts[-1]
    if isinstance(current, list):
        item_index = int(final)
        while len(current) <= item_index:
            current.append(None)
        current[item_index] = value
    else:
        current[final] = value

    return root


def scan_targets(locale_dir: Path, base_file: Path, target_codes: str | None) -> List[str]:
    if target_codes:
        return [code.strip().lower() for code in target_codes.split(",") if code.strip()]

    return sorted(
        path.stem.lower()
        for path in locale_dir.glob("*.json")
        if path.name.lower() != base_file.name.lower() and not path.name.startswith(".")
    )


def analyze(args: argparse.Namespace) -> int:
    locale_dir = Path(args.locale_dir)
    base_file = locale_dir / args.base
    if not base_file.exists():
        print(f"Base file not found: {base_file}", file=sys.stderr)
        return 2

    base_content = load_json(base_file)
    target_codes = scan_targets(locale_dir, base_file, args.targets)
    if not target_codes:
        print("No target locale files found. Pass --targets to create new languages.", file=sys.stderr)
        return 2

    base_tasks = extract_strings(base_content)
    manifest: JsonObject = {
        "baseFile": str(base_file),
        "localeDir": str(locale_dir),
        "targets": [],
    }

    total_missing = 0
    for language in target_codes:
        target_file = locale_dir / f"{language}.json"
        target_content = load_json(target_file) if target_file.exists() else {}
        missing = []

        for parts, source in base_tasks:
            current = get_at_path(target_content, parts)
            if not isinstance(current, str) or not current.strip():
                missing.append({"key": path_key(parts), "path": parts, "source": source})

        total_missing += len(missing)
        manifest["targets"].append(
            {
                "language": language,
                "file": str(target_file),
                "exists": target_file.exists(),
                "missingCount": len(missing),
                "missing": missing,
            }
        )

    if args.output:
        write_json(Path(args.output), manifest)
    else:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))

    print(f"Analyzed {len(target_codes)} target(s), {total_missing} missing item(s).", file=sys.stderr)
    return 0


def build_manifest(locale_dir: Path, base_name: str, targets: str | None) -> JsonObject:
    base_file = locale_dir / base_name
    if not base_file.exists():
        raise FileNotFoundError(f"Base file not found: {base_file}")

    base_content = load_json(base_file)
    target_codes = scan_targets(locale_dir, base_file, targets)
    if not target_codes:
        raise ValueError("No target locale files found. Pass --targets to create new languages.")

    base_tasks = extract_strings(base_content)
    manifest: JsonObject = {
        "baseFile": str(base_file),
        "localeDir": str(locale_dir),
        "targets": [],
    }

    for language in target_codes:
        target_file = locale_dir / f"{language}.json"
        target_content = load_json(target_file) if target_file.exists() else {}
        missing = []

        for parts, source in base_tasks:
            current = get_at_path(target_content, parts)
            if not isinstance(current, str) or not current.strip():
                missing.append({"key": path_key(parts), "path": parts, "source": source})

        manifest["targets"].append(
            {
                "language": language,
                "file": str(target_file),
                "exists": target_file.exists(),
                "missingCount": len(missing),
                "missing": missing,
            }
        )

    return manifest


def flatten_manifest(manifest: JsonObject) -> Dict[str, List[JsonObject]]:
    tasks_by_language: Dict[str, List[JsonObject]] = {}
    for target in manifest.get("targets", []):
        if not isinstance(target, dict):
            continue
        language = str(target.get("language", "")).strip().lower()
        missing = target.get("missing", [])
        if language and isinstance(missing, list):
            tasks_by_language[language] = [item for item in missing if isinstance(item, dict)]
    return tasks_by_language


def build_translation_prompt(tasks: List[JsonObject], target_lang: str) -> str:
    target_name = LANG_NAMES.get(target_lang, target_lang)
    data = [{"key": task["key"], "text": task["source"]} for task in tasks]

    return f"""任务：将以下英文文本翻译成{target_name}

**翻译内容：**
{json.dumps(data, ensure_ascii=False, indent=2)}

**返回格式要求：**
请严格按照以下JSON格式返回，不要包含任何其他文字：

```json
{{
  "translations": [
    {{"key": "key1", "text": "翻译文本1"}},
    {{"key": "key2", "text": "翻译文本2"}}
  ]
}}
```

**翻译要求：**
1. 准确翻译为{target_name}
2. 保持界面文本的简洁性
3. 保持原有格式和标点符号风格
4. 保持变量、占位符、HTML/XML 标签、换行和空白结构不变
5. 只返回 JSON，不要返回 Markdown、解释或额外文字"""


def extract_text_from_anthropic_response(data: Any) -> str:
    content = data.get("content") if isinstance(data, dict) else None
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(str(item.get("text", "")))
        return "\n".join(texts)
    if isinstance(data, dict) and isinstance(data.get("answer"), str):
        return data["answer"]
    return json.dumps(data, ensure_ascii=False)


def strip_json_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def parse_batch_response(text: str, original_tasks: List[JsonObject]) -> List[JsonObject]:
    parsed = json.loads(strip_json_fence(text))
    translations = parsed.get("translations") if isinstance(parsed, dict) else None
    if not isinstance(translations, list):
        raise ValueError("AI response does not contain translations array.")

    by_key = {
        str(item.get("key")): item.get("text")
        for item in translations
        if isinstance(item, dict) and isinstance(item.get("text"), str) and item.get("text", "").strip()
    }

    results = []
    for task in original_tasks:
        text_value = by_key.get(task["key"])
        if isinstance(text_value, str) and text_value.strip():
            results.append({"key": task["key"], "text": text_value, "success": True})
        else:
            results.append({"key": task["key"], "text": task["source"], "success": False})
    return results


def call_anthropic(prompt: str, args: argparse.Namespace, batch_id: str) -> str:
    token = args.auth_token
    if not token:
        searched = [str(path) for path in default_config_paths()]
        raise RuntimeError(
            "Missing API key. Set authToken in config.json, pass --auth-token, "
            f"set ANTHROPIC_AUTH_TOKEN, or set {CONFIG_ENV_NAME}. "
            f"Default config paths: {searched}"
        )

    base_url = args.base_url.rstrip("/")
    model = args.model
    endpoint = f"{base_url}/v1/messages"
    payload = {
        "model": model,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": token,
        "Authorization": f"Bearer {token}",
    }

    request = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
    start = time.time()
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{batch_id} HTTP {error.code}: {detail[:500]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"{batch_id} request failed: {error.reason}") from error

    elapsed = int((time.time() - start) * 1000)
    print(f"[{batch_id}] AI response received in {elapsed}ms", file=sys.stderr)
    return extract_text_from_anthropic_response(json.loads(response_body))


def translate_batch(tasks: List[JsonObject], target_lang: str, args: argparse.Namespace, batch_id: str) -> List[JsonObject]:
    if not tasks:
        return []

    start = time.time()
    prompt = build_translation_prompt(tasks, target_lang)
    prompt_kb = len(prompt.encode("utf-8")) / 1024
    if prompt_kb > args.max_prompt_kb:
        raise ValueError(f"{batch_id} prompt is too large: {prompt_kb:.2f}KB > {args.max_prompt_kb}KB")

    print(f"[{batch_id}] translating {len(tasks)} item(s) to {target_lang}, prompt={prompt_kb:.2f}KB", file=sys.stderr)
    last_error: Exception | None = None

    for attempt in range(1, args.retries + 2):
        try:
            text = call_anthropic(prompt, args, batch_id)
            results = parse_batch_response(text, tasks)
            success = sum(1 for item in results if item["success"])
            elapsed = int((time.time() - start) * 1000)
            print(f"[{batch_id}] done: success={success}, failed={len(results) - success}, elapsed={elapsed}ms", file=sys.stderr)
            return results
        except Exception as error:  # noqa: BLE001 - keep CLI resilient and retry.
            last_error = error
            print(f"[{batch_id}] attempt {attempt} failed: {error}", file=sys.stderr)
            if attempt <= args.retries:
                time.sleep(args.retry_delay / 1000)

    print(f"[{batch_id}] failed after retries; falling back to source text", file=sys.stderr)
    return [{"key": task["key"], "text": task["source"], "success": False} for task in tasks]


def determine_concurrency(total_tasks: int, args: argparse.Namespace) -> int:
    if total_tasks < args.concurrency_threshold:
        return 1
    return args.max_concurrency


def calculate_dynamic_batch_size(total_tasks: int, concurrency: int, max_batch_size: int) -> int:
    ideal_batch_size = (total_tasks + concurrency - 1) // concurrency
    return min(max_batch_size, max(1, ideal_batch_size))


def translate_tasks(tasks: List[JsonObject], target_lang: str, args: argparse.Namespace) -> Dict[str, str]:
    concurrency = determine_concurrency(len(tasks), args)
    dynamic_batch_size = calculate_dynamic_batch_size(len(tasks), concurrency, args.batch_size)
    result: Dict[str, str] = {}
    remaining = list(tasks)
    completed = 0
    round_number = 1
    batch_times: List[Dict[str, Any]] = []
    session_id = f"translate-{target_lang}-{int(time.time() * 1000)}"

    print(
        f"[{session_id}] total={len(tasks)}, concurrency={concurrency}, dynamicBatchSize={dynamic_batch_size}",
        file=sys.stderr,
    )

    while remaining:
        round_start = time.time()
        round_batches = []
        for _ in range(concurrency):
            if not remaining:
                break
            batch_size = min(dynamic_batch_size, len(remaining))
            round_batches.append(remaining[:batch_size])
            del remaining[:batch_size]

        print(f"[{session_id}] round {round_number}: {len(round_batches)} batch(es)", file=sys.stderr)
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(round_batches)) as executor:
            futures = []
            for index, batch in enumerate(round_batches, start=1):
                batch_id = f"{target_lang}-round{round_number}-batch{index}"
                futures.append((batch_id, batch, executor.submit(translate_batch, batch, target_lang, args, batch_id)))

            successful_batches = 0
            round_items = 0
            for batch_id, batch, future in futures:
                batch_start = time.time()
                batch_results = future.result()
                round_items += len(batch)
                success_count = 0
                for item in batch_results:
                    if item.get("success"):
                        result[item["key"]] = item["text"]
                        success_count += 1
                successful_batches += 1 if success_count else 0
                batch_times.append(
                    {
                        "batchId": batch_id,
                        "items": len(batch),
                        "time": int((time.time() - batch_start) * 1000),
                        "success": bool(success_count),
                    }
                )

        completed += round_items
        round_time = int((time.time() - round_start) * 1000)
        print(
            f"[{session_id}] round {round_number} done: successfulBatches={successful_batches}/{len(round_batches)}, "
            f"completed={completed}/{len(tasks)}, elapsed={round_time}ms",
            file=sys.stderr,
        )
        round_number += 1

        if remaining:
            actual_delay = max(500, args.delay_between_batches / 2 if concurrency > 1 else args.delay_between_batches)
            print(f"[{session_id}] delay {int(actual_delay)}ms", file=sys.stderr)
            time.sleep(actual_delay / 1000)

    if batch_times:
        avg = sum(item["time"] for item in batch_times) / len(batch_times)
        print(f"[{session_id}] finished: translated={len(result)}, avgBatchTime={avg:.0f}ms", file=sys.stderr)
    return result


def normalize_translations(data: Any) -> Dict[str, Dict[str, str]]:
    normalized: Dict[str, Dict[str, str]] = {}

    if isinstance(data, dict) and isinstance(data.get("translations"), list):
        for item in data["translations"]:
            if not isinstance(item, dict):
                continue
            language = str(item.get("language", "")).strip().lower()
            key = str(item.get("key", "")).strip()
            text = item.get("text")
            if language and key and isinstance(text, str) and text.strip():
                normalized.setdefault(language, {})[key] = text
        return normalized

    if isinstance(data, dict):
        for language, values in data.items():
            if not isinstance(values, dict):
                continue
            for key, text in values.items():
                if isinstance(text, str) and text.strip():
                    normalized.setdefault(str(language).lower(), {})[str(key)] = text

    return normalized


def apply_translations(args: argparse.Namespace) -> int:
    locale_dir = Path(args.locale_dir)
    translations = normalize_translations(load_json(Path(args.translations_json)))
    if not translations:
        print("No valid translations found.", file=sys.stderr)
        return 2

    changed_files = 0
    for language, values in translations.items():
        target_file = locale_dir / f"{language}.json"
        target_content = load_json(target_file) if target_file.exists() else {}

        if args.backup and target_file.exists():
            shutil.copy2(target_file, target_file.with_suffix(target_file.suffix + ".bak"))

        changed = 0
        for key, text in values.items():
            parts = key.split(".")
            current = get_at_path(target_content, parts)
            if args.overwrite or not isinstance(current, str) or not current.strip():
                target_content = set_at_path(target_content, parts, text)
                changed += 1

        if changed:
            write_json(target_file, target_content)
            changed_files += 1
            print(f"{target_file}: applied {changed} translation(s)")
        else:
            print(f"{target_file}: no changes")

    print(f"Changed {changed_files} file(s).")
    return 0


def translate(args: argparse.Namespace) -> int:
    apply_runtime_config(args)
    locale_dir = Path(args.locale_dir)
    manifest = build_manifest(locale_dir, args.base, args.targets)
    tasks_by_language = flatten_manifest(manifest)
    all_translations: Dict[str, Dict[str, str]] = {}

    total_missing = sum(len(tasks) for tasks in tasks_by_language.values())
    if total_missing == 0:
        print("All target locale files are up to date.")
        return 0

    print(f"Found {total_missing} missing item(s) across {len(tasks_by_language)} target(s).", file=sys.stderr)
    for language, tasks in tasks_by_language.items():
        if not tasks:
            print(f"[{language}] already up to date", file=sys.stderr)
            continue
        translated = translate_tasks(tasks, language, args)
        if translated:
            all_translations[language] = translated

    if args.translations_output:
        write_json(Path(args.translations_output), all_translations)

    if not args.no_apply and all_translations:
        apply_args = argparse.Namespace(
            locale_dir=args.locale_dir,
            translations_json=args.translations_output,
            backup=args.backup,
            overwrite=False,
        )
        if not args.translations_output:
            temp_file = Path(args.locale_dir) / ".i18n-translations.tmp.json"
            write_json(temp_file, all_translations)
            apply_args.translations_json = str(temp_file)
            try:
                return apply_translations(apply_args)
            finally:
                temp_file.unlink(missing_ok=True)
        return apply_translations(apply_args)

    print(json.dumps(all_translations, ensure_ascii=False, indent=2))
    return 0


def test_api(args: argparse.Namespace) -> int:
    apply_runtime_config(args)
    prompt = (
        "请只返回 JSON：{\"translations\":[{\"key\":\"common.save\",\"text\":\"保存\"}]}。"
        "不要返回 Markdown。"
    )
    text = call_anthropic(prompt, args, "api-test")
    parsed = json.loads(strip_json_fence(text))
    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Find missing translations.")
    analyze_parser.add_argument("locale_dir")
    analyze_parser.add_argument("--base", default="en.json")
    analyze_parser.add_argument("--targets", help="Comma-separated target language codes.")
    analyze_parser.add_argument("--output", help="Write manifest to a JSON file.")
    analyze_parser.set_defaults(func=analyze)

    apply_parser = subparsers.add_parser("apply", help="Apply translated values.")
    apply_parser.add_argument("locale_dir")
    apply_parser.add_argument("translations_json")
    apply_parser.add_argument("--backup", action="store_true")
    apply_parser.add_argument("--overwrite", action="store_true")
    apply_parser.set_defaults(func=apply_translations)

    translate_parser = subparsers.add_parser("translate", help="Analyze, batch-translate, and optionally apply.")
    translate_parser.add_argument("locale_dir")
    translate_parser.add_argument("--base", default="en.json")
    translate_parser.add_argument("--targets", help="Comma-separated target language codes.")
    translate_parser.add_argument("--translations-output", help="Write translated mapping to this JSON file.")
    translate_parser.add_argument("--no-apply", action="store_true", help="Only output translations; do not update locale files.")
    translate_parser.add_argument("--backup", action="store_true")
    translate_parser.add_argument("--batch-size", type=int)
    translate_parser.add_argument("--delay-between-batches", type=int)
    translate_parser.add_argument("--max-concurrency", type=int)
    translate_parser.add_argument("--concurrency-threshold", type=int)
    translate_parser.add_argument("--max-prompt-kb", type=float)
    translate_parser.add_argument("--config", help="Path to config JSON. Defaults to skill config.json or ~/.codex/i18n-translator/config.json.")
    translate_parser.add_argument("--base-url")
    translate_parser.add_argument("--auth-token")
    translate_parser.add_argument("--model")
    translate_parser.add_argument("--timeout", type=int)
    translate_parser.add_argument("--max-tokens", type=int)
    translate_parser.add_argument("--temperature", type=float)
    translate_parser.add_argument("--retries", type=int)
    translate_parser.add_argument("--retry-delay", type=int)
    translate_parser.set_defaults(func=translate)

    test_parser = subparsers.add_parser("test-api", help="Test the Anthropic-compatible translation API.")
    test_parser.add_argument("--config", help="Path to config JSON. Defaults to skill config.json or ~/.codex/i18n-translator/config.json.")
    test_parser.add_argument("--base-url")
    test_parser.add_argument("--auth-token")
    test_parser.add_argument("--model")
    test_parser.add_argument("--timeout", type=int)
    test_parser.add_argument("--max-tokens", type=int)
    test_parser.add_argument("--temperature", type=float)
    test_parser.add_argument("--retries", type=int)
    test_parser.add_argument("--retry-delay", type=int)
    test_parser.set_defaults(func=test_api)

    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        return args.func(args)
    except Exception as error:  # noqa: BLE001 - keep CLI output concise for agents and users.
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
