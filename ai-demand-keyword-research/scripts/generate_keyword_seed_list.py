#!/usr/bin/env python3
"""从本地 models 能力资料和词根列表生成需求关键词候选。"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Family:
    key: str
    label: str
    evidence: tuple[str, ...]
    templates: tuple[str, ...]


FAMILIES = (
    Family(
        key="assistant",
        label="通用助手 / 自动化",
        evidence=("assistant", "copilot", "chat", "agent", "自动化", "聊天", "llm", "大语言模型"),
        templates=(
            "{root} ai assistant",
            "{root} copilot",
            "ai {root} assistant",
            "{root} automation tool",
        ),
    ),
    Family(
        key="coding",
        label="代码生成 / Copilot",
        evidence=("code", "coder", "coding", "codex", "代码生成", "代码", "api", "devstral", "codestral"),
        templates=(
            "{root} code generator",
            "{root} coding assistant",
            "{root} api builder",
            "{root} developer copilot",
        ),
    ),
    Family(
        key="image-generation",
        label="图像生成",
        evidence=("图像生成", "文生图", "image generation", "text-to-image", "photo generator", "logo generator"),
        templates=(
            "{root} image generator",
            "ai {root} generator",
            "{root} photo generator",
            "{root} logo generator",
        ),
    ),
    Family(
        key="image-editing",
        label="图像编辑 / 增强",
        evidence=("图像编辑", "image editing", "background removal", "超分", "upscale", "background removal", "restore"),
        templates=(
            "{root} photo editor",
            "{root} image enhancer",
            "{root} background remover",
            "ai {root} editor",
        ),
    ),
    Family(
        key="video-generation",
        label="视频生成",
        evidence=("视频生成", "文生视频", "图生视频", "text-to-video", "image-to-video", "video generator"),
        templates=(
            "{root} video generator",
            "ai {root} video maker",
            "{root} text to video",
            "{root} image to video",
        ),
    ),
    Family(
        key="video-editing",
        label="视频编辑 / 混剪",
        evidence=("视频编辑", "video editing", "extend-video", "retake-video", "video-to-video", "motion-control"),
        templates=(
            "{root} video editor",
            "{root} clip maker",
            "{root} video enhancer",
            "{root} video remix tool",
        ),
    ),
    Family(
        key="speech-audio",
        label="语音 / 转写 / 声音克隆",
        evidence=("text-to-speech", "speech-to-text", "tts", "transcribe", "voice clone", "语音", "音频", "转录"),
        templates=(
            "{root} text to speech",
            "{root} speech to text",
            "{root} voice generator",
            "{root} voice clone",
        ),
    ),
    Family(
        key="music-sfx",
        label="音乐 / 音效",
        evidence=("music", "音效", "音乐生成", "sound effect", "stable-audio", "beatoven"),
        templates=(
            "{root} music generator",
            "{root} soundtrack generator",
            "{root} sound effect generator",
            "{root} audio enhancer",
        ),
    ),
    Family(
        key="ocr-doc",
        label="OCR / 文档解析",
        evidence=("ocr", "document", "pdf", "invoice", "文档", "文字识别", "parser", "extract"),
        templates=(
            "{root} ocr",
            "{root} document parser",
            "{root} pdf extractor",
            "{root} invoice extractor",
        ),
    ),
    Family(
        key="avatar",
        label="虚拟人 / 口型同步",
        evidence=("avatar", "lipsync", "虚拟人", "口型同步", "talking avatar", "presenter"),
        templates=(
            "{root} avatar generator",
            "{root} talking avatar",
            "{root} lipsync video",
            "{root} ai presenter",
        ),
    ),
    Family(
        key="vector-3d",
        label="3D / SVG / Lottie",
        evidence=("3d", "svg", "lottie", "矢量图", "动画", "retexture", "vecglypher", "omnilottie"),
        templates=(
            "{root} 3d generator",
            "{root} svg generator",
            "{root} lottie generator",
            "{root} vector generator",
        ),
    ),
    Family(
        key="vision-detection",
        label="视觉理解 / 检测",
        evidence=("vision", "detection", "segmentation", "caption", "nsfw", "目标检测", "分割", "图像描述"),
        templates=(
            "{root} image classifier",
            "{root} object detection",
            "{root} image caption generator",
            "{root} content moderation tool",
        ),
    ),
)

HEADER_WORDS = {
    "词根",
    "序号",
    "notes",
    "note",
    "备注",
    "加载中",
    "只能阅读",
    "菜单",
    "溢出",
    "筛选",
    "查找",
}

FAMILY_HINTS = {
    "image-generation": {
        "photo",
        "image",
        "logo",
        "design",
        "portrait",
        "avatar",
        "product",
        "listing",
        "real estate",
        "travel",
        "food",
        "fashion",
        "poster",
        "thumbnail",
        "art",
        "illustration",
        "interior",
    },
    "image-editing": {
        "photo",
        "image",
        "logo",
        "product",
        "portrait",
        "avatar",
        "thumbnail",
        "listing",
        "real estate",
        "headshot",
        "screenshot",
    },
    "video-generation": {
        "video",
        "clip",
        "reel",
        "short",
        "podcast",
        "avatar",
        "subtitle",
        "real estate",
        "listing",
        "travel",
        "ugc",
        "ad",
        "commercial",
        "training",
        "course",
        "presentation",
        "product",
        "marketing",
    },
    "video-editing": {
        "video",
        "clip",
        "reel",
        "short",
        "podcast",
        "subtitle",
        "avatar",
        "real estate",
        "listing",
        "interview",
        "webinar",
        "presentation",
    },
    "speech-audio": {
        "voice",
        "audio",
        "speech",
        "podcast",
        "subtitle",
        "meeting",
        "call",
        "interview",
        "lecture",
        "transcript",
        "note",
        "notes",
    },
    "music-sfx": {
        "music",
        "song",
        "sound",
        "audio",
        "podcast",
        "video",
        "ad",
        "commercial",
        "trailer",
        "reel",
    },
    "ocr-doc": {
        "invoice",
        "resume",
        "contract",
        "document",
        "pdf",
        "receipt",
        "form",
        "note",
        "notes",
        "meeting",
        "statement",
        "id",
        "passport",
        "bill",
        "manual",
    },
    "avatar": {
        "avatar",
        "spokesperson",
        "presenter",
        "ugc",
        "real estate",
        "sales",
        "tutor",
        "coach",
        "training",
        "educator",
        "explainer",
        "influencer",
        "host",
    },
    "vector-3d": {
        "3d",
        "svg",
        "lottie",
        "logo",
        "icon",
        "avatar",
        "game",
        "interior",
        "product",
        "furniture",
        "real estate",
    },
    "vision-detection": {
        "image",
        "photo",
        "video",
        "screen",
        "camera",
        "safety",
        "moderation",
        "product",
        "defect",
        "surveillance",
        "quality",
    },
    "coding": {
        "api",
        "app",
        "bot",
        "agent",
        "workflow",
        "code",
        "coding",
        "developer",
        "script",
        "plugin",
        "website",
        "saas",
    },
}


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="ignore")


def clean_token(token: str) -> str:
    token = token.strip()
    token = re.sub(r"^[\-\*\d\.\)\(]+", "", token).strip()
    token = token.strip("|")
    token = token.strip("`'\"[]【】()（）")
    token = re.sub(r"\s+", " ", token)
    return token


def should_keep_root(token: str) -> bool:
    lowered = token.lower()
    if not token or lowered in HEADER_WORDS:
        return False
    if lowered.startswith("http://") or lowered.startswith("https://"):
        return False
    if re.fullmatch(r"[-\d.%]+", token):
        return False
    if len(token) < 2 or len(token) > 80:
        return False
    return True


def extract_roots(raw_text: str) -> list[str]:
    roots: list[str] = []
    seen: set[str] = set()

    for line in raw_text.replace("\r", "").splitlines():
        parts: Iterable[str]
        if "|" in line:
            parts = [cell for cell in line.split("|") if cell.strip()]
        else:
            parts = re.split(r"[\t,，;；]+", line)

        for part in parts:
            token = clean_token(part)
            if not should_keep_root(token):
                continue
            key = token.casefold()
            if key in seen:
                continue
            seen.add(key)
            roots.append(token)

    return roots


def scan_model_capabilities(models_dir: Path) -> list[dict[str, object]]:
    files = sorted(models_dir.rglob("*.md"))
    if not files:
        raise SystemExit(f"未找到 Markdown 文件: {models_dir}")

    active: list[dict[str, object]] = []
    for family in FAMILIES:
        count = 0
        labels: list[str] = []
        sources: set[str] = set()
        for file_path in files:
            text = read_text(file_path).lower()
            for needle in family.evidence:
                hit = text.count(needle.lower())
                if hit:
                    count += hit
                    labels.append(needle)
                    sources.add(file_path.name)
        if count:
            active.append(
                {
                    "family": family,
                    "count": count,
                    "labels": sorted(set(labels))[:8],
                    "sources": sorted(sources),
                }
            )

    return active or [
        {
            "family": family,
            "count": 0,
            "labels": [],
            "sources": [],
        }
        for family in FAMILIES
    ]


def normalize_keyword(keyword: str) -> str:
    keyword = keyword.lower()
    keyword = re.sub(r"[^a-z0-9\s-]", " ", keyword)
    keyword = re.sub(r"\s+", " ", keyword).strip()
    return keyword


def family_matches_root(family_key: str, root: str) -> bool:
    if family_key == "assistant":
        return True
    root_text = normalize_keyword(root)
    hints = FAMILY_HINTS.get(family_key, set())
    return any(hint in root_text for hint in hints)


def dedupe_words(keyword: str) -> str:
    words = keyword.split()
    cleaned: list[str] = []
    for word in words:
        if cleaned and cleaned[-1] == word:
            continue
        cleaned.append(word)
    return " ".join(cleaned)


def generate_candidates(roots: list[str], active_families: list[dict[str, object]], limit: int) -> list[dict[str, str]]:
    family_buckets: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    seen_keywords: set[str] = set()

    ordered_families: list[dict[str, object]] = []
    active_by_key = {item["family"].key: item for item in active_families}  # type: ignore[index]
    for family in FAMILIES:
        item = active_by_key.get(family.key)
        if item:
            ordered_families.append(item)

    for item in ordered_families:
        family: Family = item["family"]  # type: ignore[assignment]
        evidence_files = ", ".join(item["sources"]) or "-"
        evidence_labels = ", ".join(item["labels"]) or "-"
        for root in roots:
            if not family_matches_root(family.key, root):
                continue
            root_text = normalize_keyword(root)
            for template in family.templates:
                keyword = template.format(root=root_text)
                keyword = dedupe_words(keyword)
                if len(keyword.split()) > 8:
                    continue
                normalized = normalize_keyword(keyword)
                if normalized in seen_keywords:
                    continue
                if normalized.startswith("ai ai "):
                    continue
                seen_keywords.add(normalized)
                family_buckets[family.key].append(
                    {
                        "keyword": keyword,
                        "root": root,
                        "capability_family": family.label,
                        "template": template,
                        "evidence_files": evidence_files,
                        "evidence_labels": evidence_labels,
                    }
                )

    selected: list[dict[str, str]] = []
    family_keys = [item["family"].key for item in ordered_families]  # type: ignore[index]
    pointers = {key: 0 for key in family_keys}

    while len(selected) < limit:
        progress = False
        for family_key in family_keys:
            bucket = family_buckets[family_key]
            pointer = pointers[family_key]
            if pointer >= len(bucket):
                continue
            selected.append(bucket[pointer])
            pointers[family_key] += 1
            progress = True
            if len(selected) >= limit:
                break
        if not progress:
            break

    return selected


def write_capability_summary(path: Path, models_dir: Path, active_families: list[dict[str, object]]) -> None:
    lines = [
        "# 模型能力摘要",
        "",
        f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> models 目录: `{models_dir}`",
        "",
        "| 能力族 | 命中次数 | 证据标签 | 来源文件 |",
        "|---|---:|---|---|",
    ]
    for item in sorted(active_families, key=lambda row: row["count"], reverse=True):  # type: ignore[index]
        family: Family = item["family"]  # type: ignore[assignment]
        labels = ", ".join(item["labels"]) or "-"  # type: ignore[index]
        sources = ", ".join(item["sources"]) or "-"  # type: ignore[index]
        lines.append(f"| {family.label} | {item['count']} | {labels} | {sources} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_seed_csv(path: Path, candidates: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "rank",
                "keyword",
                "root",
                "capability_family",
                "template",
                "evidence_files",
                "evidence_labels",
            ],
        )
        writer.writeheader()
        for index, row in enumerate(candidates, start=1):
            writer.writerow({"rank": index, **row})


def write_seed_txt(path: Path, candidates: list[dict[str, str]]) -> None:
    content = "\n".join(row["keyword"] for row in candidates) + "\n"
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 AI 需求关键词候选")
    parser.add_argument("--models-dir", required=True, help="本地 models 目录")
    parser.add_argument("--roots-file", help="词根文件，支持 txt/csv/md 纯文本")
    parser.add_argument("--roots-text", help="直接传入词根原文")
    parser.add_argument("--count", type=int, default=100, help="目标关键词数量，默认 100")
    parser.add_argument("--output-prefix", required=True, help="输出前缀，例如 /tmp/ai-demand-keywords")
    args = parser.parse_args()
    if not args.roots_file and not args.roots_text:
        parser.error("必须提供 --roots-file 或 --roots-text")
    return args


def main() -> None:
    args = parse_args()
    models_dir = Path(args.models_dir).expanduser().resolve()
    output_prefix = Path(args.output_prefix).expanduser()

    raw_roots = ""
    if args.roots_file:
        raw_roots += read_text(Path(args.roots_file).expanduser().resolve()) + "\n"
    if args.roots_text:
        raw_roots += args.roots_text

    roots = extract_roots(raw_roots)
    if not roots:
        raise SystemExit("未提取到有效词根，请检查飞书复制内容或 roots 文件。")

    active_families = scan_model_capabilities(models_dir)
    candidates = generate_candidates(roots, active_families, args.count)
    if not candidates:
        raise SystemExit("未生成任何关键词候选，请检查词根质量。")

    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    capability_path = output_prefix.with_name(output_prefix.name + "-capabilities.md")
    seed_csv_path = output_prefix.with_name(output_prefix.name + "-seeds.csv")
    seed_txt_path = output_prefix.with_name(output_prefix.name + "-seeds.txt")

    write_capability_summary(capability_path, models_dir, active_families)
    write_seed_csv(seed_csv_path, candidates)
    write_seed_txt(seed_txt_path, candidates)

    print(f"已提取词根: {len(roots)}")
    print(f"已生成候选词: {len(candidates)}")
    print(f"能力摘要: {capability_path}")
    print(f"候选词 CSV: {seed_csv_path}")
    print(f"候选词 TXT: {seed_txt_path}")


if __name__ == "__main__":
    main()
