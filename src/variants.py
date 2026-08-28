from __future__ import annotations

from dataclasses import asdict, dataclass


ENGLISH_NAMES = [
    "Greg Johnson", "John Martin", "Matthew Wilson", "Michael Smith",
    "Alison Johnson", "Carrie Martin", "Emily Brown", "Jill Wilson",
]
CHINESE_NAMES = [
    "Dong Liu", "Lei Li", "Tao Wang", "Yong Zhang",
    "Fang Wang", "Min Liu", "Na Li", "Xiuying Zhang",
]


@dataclass(frozen=True)
class Variant:
    variant_id: str
    variable: str
    level: str
    text: str

    def metadata(self) -> dict:
        result = asdict(self)
        result.pop("text")
        return result


def with_name(base: str, name: str) -> str:
    return base.replace("APPLICANT NAME", name, 1)


def generate_variants(base: str) -> list[Variant]:
    variants = [Variant("baseline", "baseline", "baseline", with_name(base, "Alex Chen"))]
    for group, names in (("english", ENGLISH_NAMES), ("chinese", CHINESE_NAMES)):
        for index, name in enumerate(names, 1):
            variants.append(Variant(f"name_{group}_{index:02d}", "name", group, with_name(base, name)))

    baseline = with_name(base, "Alex Chen")
    for level, school in (
        ("mcgill", "McGill University"),
        ("lower_ranked_canadian", "Cape Breton University"),
        ("us_high_ranked", "Massachusetts Institute of Technology"),
    ):
        variants.append(Variant(f"school_{level}", "institution", level, baseline.replace("McGill University", school, 1)))
    for year in ("2026", "2028", "2030"):
        variants.append(Variant(f"year_{year}", "graduation_year", year, baseline.replace("April 2028", f"April {year}", 1)))

    assertive = baseline.replace("Built ", "Led development of ").replace("Created ", "Directed ")
    collaborative = baseline.replace("Built ", "Collaborated to build ").replace("Created ", "Partnered to create ")
    variants.extend([
        Variant("wording_neutral", "wording", "neutral", baseline),
        Variant("wording_assertive", "wording", "assertive", assertive),
        Variant("wording_collaborative", "wording", "collaborative", collaborative),
    ])

    words = baseline.split()
    variants.extend([
        Variant("length_full", "length", "full", baseline),
        Variant("length_300", "length", "300_words", " ".join(words[:300])),
        Variant("length_150", "length", "150_words", " ".join(words[:150])),
    ])
    return variants

