#!/usr/bin/env python3
"""Export a documented, privacy-conscious JD corpus from ApplyPilot JSON."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


OUTPUT_FIELDS = (
    "jd_id",
    "company",
    "title",
    "category",
    "text",
    "word_count",
    "source_date",
)

BOILERPLATE_HEADINGS = re.compile(
    r"^(about (us|the company)|who we are|why join us|benefits|compensation|"
    r"equal (employment|opportunity)|eeo|diversity(, equity(,? and inclusion)?)?|"
    r"how to apply|application process|accommodation|privacy notice|legal)$",
    re.IGNORECASE,
)

BOILERPLATE_PHRASES = re.compile(
    r"equal opportunity employer|without regard to race|reasonable accommodation|"
    r"we celebrate diversity|we are committed to (creating|providing|building) an inclusive|"
    r"benefits may include|salary range|compensation range|apply (now|today)",
    re.IGNORECASE,
)

CATEGORY_RULES = {
    "data": re.compile(r"\b(data|analytics|machine learning|ml|ai|scientist)\b", re.I),
    "consulting": re.compile(r"\b(consult|advisory|strategy|transformation)\b", re.I),
    "product": re.compile(r"\b(product manager|product management|product owner)\b", re.I),
    "swe": re.compile(
        r"\b(software|developer|engineer|engineering|full[- ]?stack|front[- ]?end|"
        r"back[- ]?end|devops|cloud)\b",
        re.I,
    ),
}


@dataclass(frozen=True)
class Rejection:
    application_id: str
    company: str
    title: str
    reason: str


def normalize_space(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_url(value: object) -> str:
    raw = normalize_space(value)
    if not raw:
        return ""
    parts = urlsplit(raw)
    query = [
        (key, val)
        for key, val in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
        and key.lower() not in {"ref", "refid", "trackingid", "trk"}
    ]
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), urlencode(query), "")
    )


def clean_description(text: object) -> str:
    normalized = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [normalize_space(line) for line in normalized.split("\n")]
    kept: list[str] = []
    skipping_section = False

    for line in lines:
        if not line:
            if kept and kept[-1] != "":
                kept.append("")
            continue

        heading_candidate = line.rstrip(":").strip()
        if len(heading_candidate.split()) <= 8 and BOILERPLATE_HEADINGS.fullmatch(heading_candidate):
            skipping_section = True
            continue

        if len(heading_candidate.split()) <= 8 and re.search(
            r"\b(responsibilities|what you('|’)ll do|qualifications|requirements|"
            r"what we('|’)re looking for|skills|experience)\b",
            heading_candidate,
            re.I,
        ):
            skipping_section = False
            kept.append(line)
            continue

        if skipping_section:
            continue
        if BOILERPLATE_PHRASES.search(line):
            continue
        kept.append(line)

    while kept and kept[-1] == "":
        kept.pop()
    return "\n".join(kept).strip()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9][a-z0-9+#.-]*", text.lower())


def content_fingerprint(text: str) -> str:
    normalized = " ".join(tokenize(text))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def shingles(text: str, size: int = 5) -> set[tuple[str, ...]]:
    tokens = tokenize(text)
    if len(tokens) < size:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i : i + size]) for i in range(len(tokens) - size + 1)}


def jaccard(left: set[tuple[str, ...]], right: set[tuple[str, ...]]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def infer_category(title: str) -> str:
    matches = [name for name, pattern in CATEGORY_RULES.items() if pattern.search(title)]
    return matches[0] if len(matches) == 1 else "unclassified"


def source_date(application: dict) -> str:
    raw = normalize_space(application.get("capturedAt") or application.get("createdAt"))
    if not raw:
        return ""
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return ""


def stable_jd_id(application: dict) -> str:
    source = normalize_url(application.get("sourceUrl"))
    if not source:
        source = "|".join(
            [
                normalize_space(application.get("company")).lower(),
                normalize_space(application.get("role")).lower(),
                normalize_space(application.get("id")),
            ]
        )
    return "jd_" + hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]


def export_records(
    applications: list[dict],
    *,
    min_words: int = 80,
    duplicate_threshold: float = 0.90,
) -> tuple[list[dict], list[Rejection]]:
    accepted: list[dict] = []
    rejections: list[Rejection] = []
    seen_urls: set[str] = set()
    seen_fingerprints: set[str] = set()
    accepted_shingles: list[set[tuple[str, ...]]] = []

    for application in applications:
        app_id = normalize_space(application.get("id"))
        company = normalize_space(application.get("company"))
        title = normalize_space(application.get("role"))
        url = normalize_url(application.get("sourceUrl"))
        text = clean_description(application.get("description"))
        word_count = len(tokenize(text))

        def reject(reason: str) -> None:
            rejections.append(Rejection(app_id, company, title, reason))

        if not text:
            reject("missing_description")
            continue
        if word_count < min_words:
            reject(f"too_short:{word_count}<{min_words}")
            continue
        if url and url in seen_urls:
            reject("duplicate_url")
            continue

        fingerprint = content_fingerprint(text)
        if fingerprint in seen_fingerprints:
            reject("duplicate_content_exact")
            continue

        candidate_shingles = shingles(text)
        similarities = [jaccard(candidate_shingles, existing) for existing in accepted_shingles]
        if similarities and max(similarities) >= duplicate_threshold:
            reject(f"duplicate_content_near:{max(similarities):.3f}")
            continue

        record = {
            "jd_id": stable_jd_id(application),
            "company": company,
            "title": title,
            "category": infer_category(title),
            "text": text,
            "word_count": word_count,
            "source_date": source_date(application),
        }
        accepted.append(record)
        if url:
            seen_urls.add(url)
        seen_fingerprints.add(fingerprint)
        accepted_shingles.append(candidate_shingles)

    return accepted, rejections


def write_csv(path: Path, rows: list[dict], fields: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_report(records: list[dict], rejections: list[Rejection], source_path: Path) -> dict:
    category_counts: dict[str, int] = {}
    for record in records:
        category = record["category"]
        category_counts[category] = category_counts.get(category, 0) + 1
    target_categories = ("swe", "data", "consulting", "product")
    return {
        "source": str(source_path),
        "accepted": len(records),
        "rejected": len(rejections),
        "category_counts": category_counts,
        "categories_meeting_minimum_20": {
            category: category_counts.get(category, 0) >= 20 for category in target_categories
        },
        "ready_for_stratified_analysis": all(
            category_counts.get(category, 0) >= 20 for category in target_categories
        ),
        "limitations": [
            "Legacy ApplyPilot records may lack capturedAt; source_date then falls back to createdAt.",
            "Title categories are deterministic heuristics and require manual review before analysis.",
            "Boilerplate cleaning is conservative and may retain or remove atypically formatted content.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/raw/jds.csv"))
    parser.add_argument("--rejections", type=Path, default=Path("data/raw/jd_rejections.csv"))
    parser.add_argument("--report", type=Path, default=Path("data/raw/quality_report.json"))
    parser.add_argument("--min-words", type=int, default=80)
    parser.add_argument("--duplicate-threshold", type=float, default=0.90)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    applications = payload.get("applications", [])
    if not isinstance(applications, list):
        raise ValueError("ApplyPilot payload must contain an applications list")

    records, rejections = export_records(
        applications,
        min_words=args.min_words,
        duplicate_threshold=args.duplicate_threshold,
    )
    write_csv(args.output, records, OUTPUT_FIELDS)
    write_csv(
        args.rejections,
        [asdict(item) for item in rejections],
        ("application_id", "company", "title", "reason"),
    )
    report = build_report(records, rejections, args.input)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
