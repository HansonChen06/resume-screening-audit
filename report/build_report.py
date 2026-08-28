#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "report" / "report.pdf"


def footer(canvas, document):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(0.65 * inch, 0.42 * inch, "Resume Screening Semantic-Match Sensitivity Audit")
    canvas.drawRightString(7.85 * inch, 0.42 * inch, f"Page {document.page}")
    canvas.restoreState()


def fmt(value, digits=4):
    return f"{value:.{digits}f}"


def main() -> None:
    results = pd.read_csv(ROOT / "data/processed/results.csv")
    pooled = results[results.scope == "pooled"].set_index("model")
    controls = json.loads((ROOT / "data/processed/controls.json").read_text())
    quality = json.loads((ROOT / "data/raw/quality_report.json").read_text())
    robust = pd.read_csv(ROOT / "data/processed/robustness.csv")

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#17324D"), spaceAfter=18))
    styles.add(ParagraphStyle(name="Subtitle", parent=styles["Normal"], alignment=TA_CENTER, fontSize=11, leading=15, textColor=colors.HexColor("#4B5563")))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading1"], textColor=colors.HexColor("#17324D"), spaceAfter=10))
    styles.add(ParagraphStyle(name="Body2", parent=styles["BodyText"], fontSize=9.5, leading=13, spaceAfter=8))
    styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontSize=11, leading=15, borderColor=colors.HexColor("#4C78A8"), borderWidth=1, borderPadding=10, backColor=colors.HexColor("#EFF6FF"), spaceAfter=12))

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=letter, rightMargin=.65*inch, leftMargin=.65*inch, topMargin=.62*inch, bottomMargin=.65*inch)
    story = []
    story += [Spacer(1, .45*inch), Paragraph("Resume Screening Semantic-Match Sensitivity Audit", styles["TitleCenter"]), Paragraph("A preregistered paired audit of identity-token sensitivity in three cosine-similarity matchers", styles["Subtitle"]), Spacer(1, .35*inch)]
    story += [Paragraph("Abstract", styles["Section"]), Paragraph(
        "We tested whether displayed-name substitutions change resume-to-job-description cosine similarity while all qualification evidence remains fixed. The frozen corpus contains 269 real public job descriptions, and each model scored eight English-name and eight Chinese-name variants per JD. TF-IDF and SVD-100 produced statistically consistent but practically tiny raw shifts (about 0.0001). MiniLM produced a mean shift of 0.0060, with 36.1% of JDs exceeding 0.01 absolute score units. These are model-score sensitivities, not evidence of employer behaviour or hiring discrimination.", styles["Body2"])]
    story += [Paragraph("Key conclusion", styles["Section"]), Paragraph(
        "Statistical significance and practical importance diverged. The two sparse/linear matchers showed near-zero raw effects despite large standardized effects, while MiniLM showed a larger but still context-dependent score shift. Identity fields should be excluded from qualification matching whenever they are not job-relevant.", styles["Callout"])]
    story += [Paragraph("Preregistration", styles["Section"]), Paragraph("Hypotheses were locked at commit 8f1e3be; the public-ATS extension was committed at 8db02d9; corpus, resume, model revision, and seed were frozen at ad837a4 before scoring code.", styles["Body2"]), PageBreak()]

    story += [Paragraph("1. Methods", styles["Section"]), Paragraph(
        "The independent unit was the job description. For each JD and model, the confirmatory difference was the mean score across eight English-name variants minus the mean across eight Chinese-name variants. Names followed the operationalization in Oreopoulos (2011). The base resume remained byte-identical apart from the displayed name.", styles["Body2"])]
    method_rows = [["Component", "Frozen specification"], ["Sample", "269 retained JDs; 53 rejected before scoring"], ["TF-IDF", "Word 1-2 grams, sublinear TF, cosine similarity"], ["SVD-100", "Rank-100 truncated SVD of frozen TF-IDF matrix"], ["Modern model", "all-MiniLM-L6-v2 revision 1110a243..."], ["Primary test", "Two-sided paired t-test over JD-level differences"], ["Multiplicity", "Benjamini-Hochberg across three model comparisons"], ["Uncertainty", "t interval for raw mean; 2,000-JD bootstrap for d_z"], ["Sensitivity", "Wilcoxon, 10,000 sign flips, split samples, 2.5% trimming"]]
    table = Table(method_rows, colWidths=[1.45*inch, 5.65*inch], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17324D")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#CBD5E1")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("FONT", (0,0), (-1,-1), "Helvetica", 8.5), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")])]))
    story += [table, Spacer(1, 12), Paragraph("Scope", styles["Section"]), Paragraph("The study audits a simplified semantic matcher. It does not reproduce a commercial ATS, observe callbacks, or identify causal discrimination. Institution, year, wording, and length variants are exploratory because they may alter relevant evidence.", styles["Body2"]), PageBreak()]

    story += [Paragraph("2. Corpus and measurement controls", styles["Section"]), Paragraph(
        f"The collector retrieved live postings from documented Greenhouse and Lever public feeds plus two ApplyPilot captures. Deterministic cleaning and duplicate rules retained {quality['accepted']} records. Category counts were {quality['category_counts']}. All four planned categories exceeded the 20-JD reporting floor.", styles["Body2"])]
    control_rows = [["Model", "Engineering mean on SWE", "Nursing mean on SWE", "Pass"]]
    labels = {"tfidf":"TF-IDF", "svd100":"SVD-100", "minilm":"MiniLM"}
    for model in ("tfidf", "svd100", "minilm"):
        row = controls["models"][model]
        control_rows.append([labels[model], fmt(row["swe_resume_mean"]), fmt(row["swe_nursing_mean"]), "Yes" if row["positive_control_pass"] else "No"])
    control_table = Table(control_rows, colWidths=[1.3*inch, 2*inch, 2*inch, .8*inch], repeatRows=1)
    control_table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17324D")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#CBD5E1")), ("ALIGN", (1,1), (-1,-1), "CENTER"), ("FONT", (0,0), (-1,-1), "Helvetica", 8.5)]))
    story += [control_table, Spacer(1, 12), Paragraph("Control interpretation", styles["Section"]), Paragraph(
        "All three instruments ranked the engineering resume above an unrelated nursing control on SWE JDs. Repeated self-similarity was 1.0 within numeric tolerance. MiniLM had the largest control separation; TF-IDF and SVD passed directionally but had compressed score ranges. SVD-100 explained 68.3% of TF-IDF variance.", styles["Body2"]), PageBreak()]

    story += [Paragraph("3. Confirmatory results", styles["Section"]), Image(str(ROOT / "figures/main_effect.png"), width=7.05*inch, height=3.95*inch)]
    result_rows = [["Model", "Mean diff. [95% CI]", "d_z [95% CI]", "FDR p", "|diff| > .01"]]
    for model in ("tfidf", "svd100", "minilm"):
        row = pooled.loc[model]
        result_rows.append([labels[model], f"{row.mean_difference:+.4f} [{row.mean_ci_low:+.4f}, {row.mean_ci_high:+.4f}]", f"{row.cohens_dz:+.2f} [{row.dz_ci_low:+.2f}, {row.dz_ci_high:+.2f}]", f"{row.p_adjusted:.2e}", f"{100*row.fraction_abs_over_0_01:.1f}%"])
    result_table = Table(result_rows, colWidths=[.85*inch, 2.05*inch, 1.75*inch, 1.2*inch, 1.05*inch], repeatRows=1)
    result_table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17324D")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#CBD5E1")), ("FONT", (0,0), (-1,-1), "Helvetica", 7.5), ("ALIGN", (1,1), (-1,-1), "CENTER")]))
    story += [result_table, Spacer(1, 8), Paragraph("The standardized TF-IDF and SVD effects are large because tiny differences were extremely consistent and their paired standard deviations were even smaller. Raw score units show that neither exceeded 0.01 for any JD; those results are statistically detectable but practically negligible under the preregistered threshold.", styles["Body2"]), PageBreak()]

    story += [Paragraph("4. Exploratory category analysis", styles["Section"]), Image(str(ROOT / "figures/category_heatmap.png"), width=7.0*inch, height=4.0*inch), Paragraph(
        "Category results are exploratory. MiniLM's direction was broadly positive but varied in magnitude, while sparse and SVD effects stayed close to zero. This heterogeneity argues against reducing the audit to a single universal bias number. The title classifier is deterministic and multilingual but still heuristic; category ambiguity remains a documented limitation.", styles["Body2"]), PageBreak()]

    story += [Paragraph("5. Robustness", styles["Section"]), Image(str(ROOT / "figures/robustness.png"), width=7.0*inch, height=4.0*inch)]
    directions = robust.groupby("model").direction.nunique().to_dict()
    story += [Paragraph(
        "The pooled direction remained unchanged in first-half, second-half, and 2.5%-trimmed analyses for each model. Wilcoxon and sign-flip sensitivity tests agreed with the paired t-test on detectability. Robustness of direction does not make a small raw effect operationally important; it only shows that the sign is not driven by one half of the corpus or a few extreme JDs.", styles["Body2"]), Paragraph("Robustness matrix summary", styles["Section"]), Paragraph("TF-IDF: direction supported in 4/4 settings. SVD-100: 4/4. MiniLM: 4/4. Exact magnitudes varied across splits.", styles["Callout"]), PageBreak()]

    story += [Paragraph("6. Limitations", styles["Section"])]
    limitations = [
        "Public ATS feeds overrepresent employers using Greenhouse or Lever and are not a probability sample of jobs.",
        "Names follow a prior Canadian audit's operational groups; a name does not determine ethnicity, culture, or identity.",
        "Cosine similarity is a research instrument, not evidence about proprietary screening systems or employer decisions.",
        "The original MATH 308 co-occurrence matrix was not recovered; SVD-100 is a method-level bridge fitted to this corpus.",
        "The modern model may encode identity associations learned from its training corpus; this audit does not identify their causal source.",
        "Raw job text is not redistributed in the public repository; exact local reproduction requires the frozen private snapshot.",
    ]
    for item in limitations:
        story.append(Paragraph(f"• {item}", styles["Body2"]))
    story += [Paragraph("7. Conclusion", styles["Section"]), Paragraph(
        "Identity-token substitutions can move semantic-match scores even when qualifications are unchanged. In this corpus, TF-IDF and SVD-100 shifts were effectively zero in raw units, while MiniLM showed a mean 0.0060 shift and crossed 0.01 for 36.1% of JDs. The engineering recommendation is simple: remove names and other non-job-relevant identity fields before matching, report raw score changes alongside standardized effects, and validate every matcher with unrelated-domain and determinism controls.", styles["Callout"]), Paragraph("References", styles["Section"]), Paragraph("Bertrand, M., and Mullainathan, S. (2004). American Economic Review 94(4), 991-1013. Oreopoulos, P. (2011). American Economic Journal: Economic Policy 3(4), 148-171. Greenhouse Job Board API documentation. Lever Postings API documentation.", styles["Body2"])]

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()

