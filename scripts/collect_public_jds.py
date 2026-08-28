#!/usr/bin/env python3
"""Freeze live public Greenhouse/Lever postings into an ApplyPilot-like snapshot."""

from __future__ import annotations

import argparse
import html
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from export_jds import infer_category


GREENHOUSE_BOARDS = {
    "2K": "2k",
    "Affirm": "affirm",
    "Asana": "asana",
    "Braze": "braze",
    "Carta": "carta",
    "Coinbase": "coinbase",
    "Confluent": "confluent",
    "Datadog": "datadog",
    "Discord": "discord",
    "Duolingo": "duolingo",
    "Figma": "figma",
    "Instacart": "instacart",
    "Lyft": "lyft",
    "MongoDB": "mongodb",
    "Okta": "okta",
    "Plaid": "plaid",
    "Ramp": "ramp",
    "Reddit": "reddit",
    "Robinhood": "robinhood",
    "Samsara": "samsara",
    "Twilio": "twilio",
    "Vimeo": "vimeo",
}

LEVER_SITES = {
    "Anduril": "anduril",
    "Highspot": "highspot",
    "Palantir": "palantir",
    "Scale AI": "scaleai",
    "Shopify": "shopify",
    "Veeva": "veeva",
}


class TextExtractor:
    TAG_RE = re.compile(r"<[^>]+>")

    @classmethod
    def clean(cls, value: str) -> str:
        value = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h[1-6]>", "\n", value or "")
        value = cls.TAG_RE.sub(" ", value)
        value = html.unescape(value)
        value = value.replace("\r\n", "\n").replace("\r", "\n")
        value = re.sub(r"[ \t]+", " ", value)
        value = re.sub(r"\n\s*\n\s*\n+", "\n\n", value)
        return value.strip()


def fetch_json(url: str) -> object:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "resume-screening-audit/1.0 (research snapshot)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def greenhouse_records(company: str, token: str, captured_at: str) -> list[dict]:
    endpoint = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    payload = fetch_json(endpoint)
    records = []
    for job in payload.get("jobs", []):
        description = TextExtractor.clean(job.get("content", ""))
        location = (job.get("location") or {}).get("name", "")
        records.append(
            {
                "id": f"greenhouse-{token}-{job.get('id')}",
                "role": job.get("title", ""),
                "company": company,
                "location": location,
                "sourceUrl": job.get("absolute_url", ""),
                "source": "greenhouse_public_api",
                "pageTitle": f"{job.get('title', '')} | {company}",
                "description": description,
                "capturedAt": captured_at,
                "createdAt": captured_at,
                "updatedAt": captured_at,
                "status": "Corpus only",
                "notes": f"Public Greenhouse Job Board API snapshot; board={token}",
                "tags": ["public-ats", "greenhouse", "real-jd"],
            }
        )
    return records


def lever_records(company: str, site: str, captured_at: str) -> list[dict]:
    endpoint = f"https://api.lever.co/v0/postings/{site}?mode=json"
    payload = fetch_json(endpoint)
    records = []
    for job in payload:
        sections = [job.get("descriptionPlain", "")]
        for section in job.get("lists", []):
            sections.append(section.get("text", ""))
            sections.append(TextExtractor.clean(section.get("content", "")))
        sections.append(job.get("additionalPlain", ""))
        records.append(
            {
                "id": f"lever-{site}-{job.get('id')}",
                "role": job.get("text", ""),
                "company": company,
                "location": (job.get("categories") or {}).get("location", ""),
                "sourceUrl": job.get("hostedUrl", ""),
                "source": "lever_public_api",
                "pageTitle": f"{job.get('text', '')} | {company}",
                "description": "\n\n".join(part.strip() for part in sections if part.strip()),
                "capturedAt": captured_at,
                "createdAt": captured_at,
                "updatedAt": captured_at,
                "status": "Corpus only",
                "notes": f"Public Lever Postings API snapshot; site={site}",
                "tags": ["public-ats", "lever", "real-jd"],
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--applypilot", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/raw/combined_applypilot.json"))
    parser.add_argument("--manifest", type=Path, default=Path("data/raw/source_manifest.json"))
    parser.add_argument("--max-per-category", type=int, default=70)
    parser.add_argument("--max-unclassified", type=int, default=40)
    args = parser.parse_args()

    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    records: list[dict] = []
    manifest = {"captured_at": captured_at, "sources": [], "failures": []}

    local = json.loads(args.applypilot.read_text(encoding="utf-8"))
    local_records = local.get("applications", [])

    for provider, sources, reader in (
        ("greenhouse", GREENHOUSE_BOARDS, greenhouse_records),
        ("lever", LEVER_SITES, lever_records),
    ):
        for company, token in sources.items():
            try:
                found = reader(company, token, captured_at)
                records.extend(found)
                manifest["sources"].append(
                    {"provider": provider, "company": company, "token": token, "records": len(found)}
                )
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as error:
                manifest["failures"].append(
                    {"provider": provider, "company": company, "token": token, "error": str(error)}
                )
            time.sleep(0.05)

    limits = {
        "swe": args.max_per_category,
        "data": args.max_per_category,
        "consulting": args.max_per_category,
        "product": args.max_per_category,
        "unclassified": args.max_unclassified,
    }
    selected = list(local_records)
    selected_counts = {name: 0 for name in limits}
    for record in sorted(records, key=lambda item: (item.get("sourceUrl", ""), item.get("id", ""))):
        category = infer_category(record.get("role", ""))
        if selected_counts[category] >= limits[category]:
            continue
        selected.append(record)
        selected_counts[category] += 1

    manifest["fetched_records"] = len(records)
    manifest["selected_records"] = len(selected)
    manifest["selected_category_counts"] = selected_counts
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"applications": selected}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(selected), **manifest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
