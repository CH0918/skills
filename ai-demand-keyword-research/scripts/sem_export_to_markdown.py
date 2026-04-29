#!/usr/bin/env python3
"""把 sem.3ue.co 导出的 CSV 转成 Markdown 表格。"""

from __future__ import annotations

import argparse
import csv
import math
import re
from datetime import datetime
from pathlib import Path


FIELD_ALIASES = {
    "keyword": {"关键词", "Keyword", "keyword"},
    "intent": {"意图", "Intent", "intent"},
    "volume": {"搜索量", "Volume", "Search Volume", "volume"},
    "kd": {"KD (%)", "Keyword Difficulty", "KD", "kd"},
    "cpc": {"CPC (USD)", "CPC", "cpc"},
    "competition": {"竞争程度", "Competition", "competition"},
    "results": {"结果", "Results", "results"},
    "updated": {"已更新", "Updated", "updated"},
}

INTENT_BONUS = {
    "信息": 5,
    "商务": 12,
    "交易": 15,
    "导航": 6,
    "informational": 5,
    "commercial": 12,
    "transactional": 15,
    "navigational": 6,
}


def detect_delimiter(sample: str) -> str:
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        return ","
    return dialect.delimiter


def open_csv(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig", errors="ignore")
    delimiter = detect_delimiter(text[:4096])
    reader = csv.DictReader(text.splitlines(), delimiter=delimiter)
    return [{(key or "").strip(): (value or "").strip() for key, value in row.items()} for row in reader]


def find_field(row: dict[str, str], logical_name: str) -> str:
    aliases = FIELD_ALIASES[logical_name]
    for key, value in row.items():
        if key.strip() in aliases:
            return value.strip()
    return ""


def parse_number(raw: str) -> float:
    if not raw:
        return 0.0
    cleaned = raw.replace("$", "").replace(",", "").replace("%", "").strip()
    multiplier = 1.0
    suffix_map = {"K": 1_000.0, "M": 1_000_000.0, "B": 1_000_000_000.0}
    if cleaned[-1:].upper() in suffix_map:
        multiplier = suffix_map[cleaned[-1].upper()]
        cleaned = cleaned[:-1]
    try:
        return float(cleaned) * multiplier
    except ValueError:
        return 0.0


def normalize_intent(raw: str) -> str:
    return raw.strip() or "-"


def load_seed_map(path: Path | None) -> dict[str, dict[str, str]]:
    if not path:
        return {}
    rows = open_csv(path)
    mapping: dict[str, dict[str, str]] = {}
    for row in rows:
        keyword = row.get("keyword", "").strip().lower()
        if keyword:
            mapping[keyword] = row
    return mapping


def opportunity_score(volume: float, kd: float, cpc: float, intent: str) -> float:
    volume_score = min(math.log10(volume + 10) * 12, 55)
    kd_score = max(0.0, 35 - kd * 0.35)
    cpc_score = min(cpc, 20.0) / 20.0 * 5.0
    intent_score = INTENT_BONUS.get(intent.casefold(), INTENT_BONUS.get(intent, 3))
    return round(volume_score + kd_score + cpc_score + intent_score, 1)


def format_int(value: float) -> str:
    return f"{int(round(value)):,}" if value else "0"


def format_float(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".") if value else "0"


def build_rows(raw_rows: list[dict[str, str]], seed_map: dict[str, dict[str, str]]) -> list[dict[str, str | float]]:
    rows: list[dict[str, str | float]] = []
    for row in raw_rows:
        keyword = find_field(row, "keyword")
        if not keyword:
            continue
        intent = normalize_intent(find_field(row, "intent"))
        volume = parse_number(find_field(row, "volume"))
        kd = parse_number(find_field(row, "kd"))
        cpc = parse_number(find_field(row, "cpc"))
        competition = parse_number(find_field(row, "competition"))
        results = parse_number(find_field(row, "results"))
        seed = seed_map.get(keyword.lower(), {})

        rows.append(
            {
                "keyword": keyword,
                "root": seed.get("root", "-"),
                "family": seed.get("capability_family", "-"),
                "intent": intent,
                "volume": volume,
                "kd": kd,
                "cpc": cpc,
                "competition": competition,
                "results": results,
                "template": seed.get("template", "-"),
                "score": opportunity_score(volume, kd, cpc, intent),
            }
        )

    rows.sort(key=lambda item: (item["score"], item["volume"], -item["kd"]), reverse=True)  # type: ignore[index]
    return rows


def write_markdown(path: Path, rows: list[dict[str, str | float]], source_path: Path) -> None:
    top_rows = rows
    avg_volume = sum(float(row["volume"]) for row in top_rows) / len(top_rows) if top_rows else 0.0
    avg_kd = sum(float(row["kd"]) for row in top_rows) / len(top_rows) if top_rows else 0.0
    avg_cpc = sum(float(row["cpc"]) for row in top_rows) / len(top_rows) if top_rows else 0.0
    easy_count = sum(1 for row in top_rows if float(row["kd"]) <= 40)

    lines = [
        "# AI 需求关键词机会汇总",
        "",
        f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 数据来源: `{source_path}`",
        f"> 关键词数量: {len(top_rows)}",
        f"> 排序方式: 机会分 = 搜索量 + 低 KD + CPC + 意图加权",
        "",
        "## 摘要",
        "",
        f"- 平均搜索量: {format_int(avg_volume)}",
        f"- 平均 KD: {format_float(avg_kd)}",
        f"- 平均 CPC: {format_float(avg_cpc)}",
        f"- 低难度词数量(KD<=40): {easy_count}",
        "",
        "## 明细",
        "",
        "| 排名 | 关键词 | 词根 | 能力族 | 意图 | 搜索量 | KD | CPC | 竞争度 | 结果数 | 机会分 |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]

    for index, row in enumerate(top_rows, start=1):
        lines.append(
            "| {rank} | {keyword} | {root} | {family} | {intent} | {volume} | {kd} | {cpc} | {competition} | {results} | {score} |".format(
                rank=index,
                keyword=row["keyword"],
                root=row["root"],
                family=row["family"],
                intent=row["intent"],
                volume=format_int(float(row["volume"])),
                kd=format_float(float(row["kd"])),
                cpc=format_float(float(row["cpc"])),
                competition=format_float(float(row["competition"])),
                results=format_int(float(row["results"])),
                score=format_float(float(row["score"])),
            )
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="把 sem CSV 导出转成 Markdown")
    parser.add_argument("--input", required=True, help="sem 导出的 CSV 文件")
    parser.add_argument("--seed-csv", help="generate_keyword_seed_list.py 输出的 seeds.csv")
    parser.add_argument("--top", type=int, default=100, help="保留前多少行，默认 100")
    parser.add_argument("--output", required=True, help="输出 Markdown 文件")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if input_path.suffix.lower() not in {".csv", ".txt"}:
        raise SystemExit("请先在 sem.3ue.co 导出 CSV，再传给本脚本。")

    seed_path = Path(args.seed_csv).expanduser().resolve() if args.seed_csv else None
    raw_rows = open_csv(input_path)
    seed_map = load_seed_map(seed_path)
    rows = build_rows(raw_rows, seed_map)[: args.top]
    if not rows:
        raise SystemExit("没有从导出文件中读到关键词行，请检查导出的 CSV。")

    output_path = Path(args.output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(output_path, rows, input_path)
    print(f"Markdown 已生成: {output_path}")


if __name__ == "__main__":
    main()
