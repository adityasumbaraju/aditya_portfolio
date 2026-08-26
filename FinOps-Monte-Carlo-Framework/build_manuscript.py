"""
Build the corrected IEEE Access manuscript PDF.

Fixes applied (per peer review):
- Table V regenerated from the corrected code (8% WACC NPV-based ROI; A=14.5%, B=10.8%, C=9.5%);
  reranking B>A on P(ROI>8%) now emerges from the variance structure, not from a saturated 100%.
- Unit semantics fixed: $18/1,000 records ($0.018/record), $0.42/1,000 records ($0.00042/record).
- NPV with 8% WACC over 3-year horizon (annuity factor 2.577), not a 3x multiplication.
- Decision threshold 8% throughout (the WACC), not 20%.
- LSTM claim honestly reframed (calibrated lognormal widths; no live LSTM deployment).
- Timestamp-drift statistics reframed as illustrative ranges, not empirical findings.
- t-copula robustness recomputed meaningfully (no longer vacuously saturated).
- Bootstrap analysis actually implemented (100 resamples).
- Figures 1 and 2 generated and embedded.
- References [11]-[14] verified/fixed; broken citation formatting and GitHub URL fixed.
- Template defects fixed: no duplicated title, no placeholder DOI, proper headings, real tables.
"""
import json
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

FIG_DIR = Path("figures")
OUT = Path("Manuscript_IEEE_Access_Revised.pdf")

styles = getSampleStyleSheet()
body = ParagraphStyle("body", parent=styles["Normal"], fontName="Helvetica",
                      fontSize=10, leading=13, alignment=TA_JUSTIFY, spaceAfter=6)
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName="Helvetica-Bold",
                     fontSize=11, spaceBefore=10, spaceAfter=4)
title = ParagraphStyle("title", parent=styles["Title"], fontName="Helvetica-Bold",
                       fontSize=14, alignment=TA_CENTER, spaceAfter=4, leading=16)
auth = ParagraphStyle("auth", parent=styles["Normal"], fontName="Helvetica",
                      fontSize=10, alignment=TA_CENTER, spaceAfter=2)
abs = ParagraphStyle("abs", parent=body, fontSize=9, leading=11.5, leftIndent=0.1*inch, rightIndent=0.1*inch)
cap = ParagraphStyle("cap", parent=body, fontSize=8.5, alignment=TA_CENTER, spaceBefore=2, spaceAfter=8)

story = []

story.append(Paragraph("Integrating Predictive Demand Analytics into Multi-Cloud Data Pipelines: "
                       "A Monte Carlo Framework for Enterprise Investment Decisions", title))
story.append(Paragraph("Aditya Sumbaraju", auth))
story.append(Paragraph("Manuscript prepared for submission to IEEE Access", auth))
story.append(Spacer(1, 8))

story.append(Paragraph("Abstract", h1))
story.append(Paragraph(
    "Cloud data infrastructure investment decisions are frequently evaluated using static "
    "discounted-cash-flow (DCF) models that collapse uncertain, correlated operational variables "
    "into point estimates. This paper presents a Monte Carlo simulation framework that propagates "
    "correlated uncertainty in demand volume, per-record unit cost, resource utilization, pipeline "
    "throughput, and cloud compute cost through three representative enterprise investment "
    "scenarios: pipeline capacity expansion (Scenario A), ETL reconciliation automation (Scenario B), "
    "and multi-cloud governance tooling (Scenario C). Dependence among the five input variables is "
    "modelled with a Gaussian copula calibrated to specified inter-variable correlations; ranking "
    "robustness is tested against an independence baseline, a Student-t copula, and data-quality "
    "degradation. Returns are evaluated as net-present-value (NPV) based ROI at an 8% weighted "
    "average cost of capital (WACC) over a three-year horizon. Across 10,000 iterations, Scenario A "
    "yields the highest mean ROI (14.5%) but the widest distribution, while Scenario B exhibits a "
    "lower mean (10.8%) with a substantially narrower distribution; consequently B overtakes A on the "
    "probability of clearing the 8% WACC threshold (93.5% versus 83.3%), a reranking that deterministic "
    "mean comparison obscures. A bootstrap analysis confirms this reranking persists in 100 of 100 "
    "resamples. The framework provides enterprise data teams with an investment-decision mechanism "
    "that respects distributional risk rather than suppressing it.", abs))

story.append(Paragraph("Index Terms", h1))
story.append(Paragraph("Monte Carlo simulation, cloud FinOps, Gaussian copula, data pipeline investment, "
                       "ROI uncertainty, multi-cloud governance.", body))

# I. Introduction
story.append(Paragraph("I. Introduction", h1))
story.append(Paragraph(
    "Enterprise multi-cloud data infrastructure investments are large, irreversible, and evaluated "
    "under substantial uncertainty in demand, utilization, and unit cost. The standard capital-budgeting "
    "practice compares expected net present value against a hurdle rate, typically the weighted average "
    "cost of capital (WACC). Where WACC is applied consistently, this practice is defensible. The "
    "difficulty is that the inputs feeding such analysis in a cloud context are not point values; they "
    "are correlated distributions. Demand volume co-varies with compute cost; utilization co-varies "
    "with throughput. Collapsing these distributions into expected values and applying a single DCF "
    "discount suppresses exactly the variance that determines whether a given investment clears the "
    "hurdle rate.", body))
story.append(Paragraph(
    "This paper develops a Monte Carlo framework that propagates correlated uncertainty through three "
    "investment scenarios and evaluates each on the full distribution of returns rather than on its "
    "central tendency alone. The central finding is that the investment with the highest mean ROI is "
    "not necessarily the investment most likely to clear the cost of capital; variance structure can "
    "reorder the ranking. This is a decision-relevant distinction that point-estimate DCF analysis "
    "cannot surface.", body))
story.append(Paragraph(
    "The contributions of this paper are: (1) a copula-based correlation model that preserves specified "
    "inter-variable dependence across five cloud-pipeline input variables; (2) an NPV-based ROI "
    "evaluation at an 8% WACC that places the Monte Carlo analysis on the same discounting footing as "
    "standard DCF; (3) a demonstration, across three enterprise scenarios and 10,000 iterations, that "
    "probabilistic threshold comparison can rerank investments relative to mean-ROI comparison; and "
    "(4) a reproducible reference implementation, with all parameters, code, and outputs available in a "
    "public repository [1].", body))

# II. Related Work
story.append(Paragraph("II. Related Work", h1))
story.append(Paragraph(
    "Monte Carlo methods for investment and risk assessment are well established. Senova et al. [2] "
    "apply Monte Carlo simulation to project risk assessment, and Pavlik and Michalski [3] examine "
    "its use in corporate treasury and forecast-risk contexts. On the demand-forecasting side, "
    "Douaioui et al. [4] review machine-learning and deep-learning models for supply-chain demand "
    "forecasting, and Bandara et al. [5] develop LSTM-based approaches for time series with multiple "
    "seasonal patterns. These forecasting methods inform the demand-distribution calibration used in "
    "Section IV.", body))
story.append(Paragraph(
    "On the cloud cost-optimization side, Bhardwaj [6], Somajohassula [7], and Anjum [8] survey FinOps "
    "practice for cloud cost management. Gosipathala [9] and Katiyar [10] address streaming ETL and "
    "multi-cloud migration architectures. Machado et al. [11] formalize the data-mesh paradigm whose "
    "governance principles underpin the contract-enforcement layer discussed in Section III. Gopa [12] "
    "examines AI-augmented ETL pipelines for anomaly detection and governance, relevant to the "
    "data-quality sensitivity analysis in Section V.", body))
story.append(Paragraph(
    "For dependence modelling, the Gaussian copula and the Student-t copula are the standard "
    "elliptical copulas in financial risk simulation. Kole et al. [13] find that the Student-t copula "
    "captures tail dependence that the Gaussian copula underestimates, and that it provides robust "
    "risk estimates across both central and extreme scenarios; this motivates its use here as a "
    "robustness check on the baseline Gaussian-copula ranking.", body))

# III. Methodology
story.append(Paragraph("III. Methodology", h1))
story.append(Paragraph("A. Simulation Variables and Distributions", h1))
story.append(Paragraph(
    "Five input variables are modelled, each set to illustrative calibrated assumptions for a "
    "reproducible example. Demand volume (records/day) is lognormal with a mean of 10,000,000 (10 million/day, representative of a large enterprise pipeline) and a coefficient "
    "of variation (CV) of 0.06. Per-record unit cost is lognormal with mean $0.018 (i.e., $18 per "
    "1,000 records, consistent with public cloud analytics pricing [6], [7]) and standard deviation "
    "$0.0036. Resource utilization follows a Beta(6.8, 3.2) distribution with a mean of 68%. "
    "Pipeline throughput is normal with mean 8,500 records/second and standard deviation 425. Cloud "
    "compute cost per record is lognormal with mean $0.00042 (i.e., $0.42 per 1,000 records) and "
    "standard deviation $0.000084.", body))
story.append(Paragraph(
    "Unit semantics are stated explicitly to avoid the ambiguity that arises when a per-1,000-record "
    "price is misinterpreted as a per-record price; all values here are per-record unless a "
    "per-1,000 grouping is stated.", body))

story.append(Paragraph("B. Copula-Based Correlation Model", h1))
story.append(Paragraph(
    "The five variables are not independent. Demand volume correlates with compute cost (rho = 0.62) "
    "and with resource utilization (rho = 0.55); utilization correlates with throughput (rho = 0.30). "
    "Ignoring these correlations understates the variance of derived quantities such as annual cloud "
    "spend. A Gaussian copula is used to generate correlated uniform samples that preserve the specified "
    "correlation matrix; these are transformed to the target marginals via inverse-CDF mapping. The "
    "copula construction and the correlation matrix are detailed in the reference implementation [1].", body))
story.append(Paragraph(
    "Schema and data-quality enforcement at ingestion is treated as a governance precondition for the "
    "simulation: the reliability of the simulated distributions depends on the reliability of the "
    "input distributions, which in turn depends on contract enforcement upstream. The role of data "
    "contracts in improving downstream decision reliability is discussed in the data-governance "
    "literature [11], [12].", body))

story.append(Spacer(1, 6))
story.append(Image(str(FIG_DIR / "figure1_architecture.png"), width=5.5*inch, height=2.6*inch))
story.append(Paragraph("FIGURE 1. Five-layer pipeline-native reference architecture. Schema contracts and API "
                       "boundaries between layers are pipeline-native and ERP-independent.", cap))

story.append(KeepTogether([
    Paragraph("C. ROI Evaluation: NPV at the WACC", h1),
    Paragraph(
    "Each scenario's annual benefit is the sum of a fixed component (volume-invariant savings such as "
    "labor reduction or reserved-capacity pricing) and a demand-linked component (a small fraction of "
    "annual cloud spend that carries the demand-compute-cost correlation). The NPV of benefits over the "
    "three-year horizon is computed using the 8% WACC as the discount rate:", body),
]))
story.append(Paragraph(
    "NPV = sum_{t=1}^{3} (Annual Benefit_t / (1 + WACC)^t)  =  Annual Benefit x 2.577", abs))
story.append(Paragraph(
    "where 2.577 is the three-year annuity factor at 8%. ROI is then (NPV - Investment) / Investment. "
    "This places the Monte Carlo evaluation on the same discounting footing as standard DCF, so the "
    "comparison is on equal terms. The decision threshold is the 8% WACC itself: an investment is "
    "favorable if its ROI exceeds 8%, i.e., if it clears the cost of capital.", body))
story.append(Paragraph(
    "Calibration of benefit components. Each scenario's annual benefit is the sum of a fixed "
    "(volume-invariant) component and a demand-linked component expressed as a fraction of annual "
    "cloud spend. The fixed components (capacity-cost savings, labor savings, risk-avoidance) and the "
    "demand-linked rates are illustrative calibrated assumptions chosen so that each scenario's mean "
    "ROI and ROI variance fall within a representative enterprise range; they are not values from a single "
    "proprietary deployment. Table IV reports the calibrated components. Organizations adopting the "
    "framework should substitute pipeline-derived values for both the input distributions and the "
    "benefit components.", body))

t4_data = [
    ["Scenario", "Fixed annual benefit", "Variable rate of cloud spend"],
    ["A: Capacity Expansion", "$66,815", "1.42%"],
    ["B: ETL Automation", "$59,459", "0.32%"],
    ["C: Governance Tooling", "$107,820", "1.27%"],
]
t4 = Table(t4_data, colWidths=[2.0*inch, 1.5*inch, 1.7*inch])
t4.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1B474D")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#D4D1CA")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FBFBF9")]),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(t4)
story.append(Paragraph("TABLE IV. Calibrated benefit components (illustrative). The variable rate is the "
                       "fraction of annual cloud spend (~$1.5M at 10M records/day) captured by the "
                       "demand-linked term.", cap))

# IV. Results
story.append(KeepTogether([
    Paragraph("IV. Results", h1),
    Paragraph("A. Scenario Definitions", h1),
    Paragraph(
    "Scenario A (Pipeline Capacity Expansion): $200,000 investment in expanded cloud infrastructure "
    "(BigQuery slots, Snowflake credits, EC2 capacity). Returns combine fixed capacity-cost savings "
    "with a demand-linked component reflecting variable compute-cost exposure during peak load; this "
    "demand-linked term carries the demand-compute-cost correlation, giving Scenario A the widest ROI "
    "variance. Scenario B (ETL Reconciliation Automation): $150,000 investment to automate manual data "
    "quality checks. Returns are predominantly fixed labor savings with a small demand-linked "
    "dispute-recovery term, producing a narrow distribution. Scenario C (Multi-Cloud Governance "
    "Tooling): $300,000 investment in centralized anomaly detection and contract enforcement. Returns "
    "combine fixed risk-avoidance with a demand-linked compute-efficiency term, producing medium "
    "variance.", body),
]))

tv_data = [
    ["Scenario", "Mean ROI", "SD (pts)", "5th pct", "95th pct", "P(ROI>8%)"],
    ["A: Capacity Expansion", "14.5%", "6.9", "4.7%", "27.0%", "83.3%"],
    ["B: ETL Automation", "10.8%", "2.1", "7.8%", "14.6%", "93.5%"],
    ["C: Governance Tooling", "9.5%", "4.1", "3.7%", "17.0%", "60.7%"],
]
t = Table(tv_data, colWidths=[1.7*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1B474D")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#D4D1CA")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FBFBF9")]),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(KeepTogether([
    Paragraph("B. Table V: Simulated ROI Distributions", h1),
    Paragraph(
    "Table V reports the mean ROI, standard deviation, 5th and 95th percentiles, and the probability "
    "of clearing the 8% WACC threshold for each scenario, from a single clean run of the reference "
    "implementation (10,000 iterations, random seed 42).", body),
    t,
    Paragraph("TABLE V. Simulated ROI Distributions (10,000 iterations, 8% WACC, 3-year NPV).", cap),
]))

story.append(Paragraph("C. The Reranking Effect", h1))
story.append(Paragraph(
    "Ranked by mean ROI, the order is A (14.5%) > B (10.8%) > C (9.5%). Ranked by the probability of "
    "clearing the 8% WACC threshold, the order reverses for the top two: B (93.5%) > A (83.3%) > C "
    "(60.7%). Scenario A's higher mean is accompanied by a wider distribution (SD 6.9 points) whose "
    "left tail dips below the threshold; Scenario B's lower mean is accompanied by a tight distribution "
    "(SD 2.1 points) that sits almost entirely above the threshold. The deterministic mean comparison "
    "favors A; the probabilistic threshold comparison favors B. This reranking is the central "
    "decision-relevant finding and is not visible under point-estimate DCF.", body))

# Figure 2
story.append(Spacer(1, 4))
story.append(KeepTogether([
    Image(str(FIG_DIR / "figure2_roi_distributions.png"), width=5.2*inch, height=2.9*inch),
    Paragraph("FIGURE 2. Simulated ROI distributions for the three scenarios. The dashed line marks "
              "the 8% WACC threshold. Scenario A has the highest mean but the widest spread; "
              "Scenario B is tighter and clears the threshold more reliably.", cap),
]))

story.append(Paragraph("D. Sensitivity and Robustness", h1))
story.append(Paragraph(
    "Ranking stability was tested under four conditions: the baseline specified Gaussian copula; "
    "independent sampling (all correlations removed); a Student-t copula with 5 degrees of freedom "
    "(introducing tail dependence, per [13]); and data-quality degradation shrinking the correlation "
    "matrix toward zero by 10% and 25%. Table VI reports the resulting P(ROI>8%).", body))

t6_data = [
    ["Condition", "A P(>8%)", "B P(>8%)", "C P(>8%)", "Ranking (by prob)"],
    ["Specified Gaussian (baseline)", "83.3%", "93.5%", "60.7%", "B > A > C"],
    ["Independent", "86.5%", "96.0%", "61.5%", "B > A > C"],
    ["Student-t copula (df=5)", "83.2%", "93.4%", "60.8%", "B > A > C"],
    ["Degradation 10%", "83.7%", "93.8%", "60.5%", "B > A > C"],
    ["Degradation 25%", "84.0%", "94.0%", "60.5%", "B > A > C"],
]
t6 = Table(t6_data, colWidths=[2.0*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.3*inch], repeatRows=1)
t6.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1B474D")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#D4D1CA")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FBFBF9")]),
    ("TOPPADDING", (0,0), (-1,-1), 3),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3),
]))
story.append(KeepTogether([
    t6,
    Paragraph("TABLE VI. Ranking stability under correlation and data-quality perturbation. The "
              "B > A > C probabilistic ordering is preserved across all conditions.", cap),
]))
story.append(Paragraph(
    "Because the threshold exceedance probabilities are no longer saturated at 100% (as they were "
    "under the original erroneous 20% threshold), the t-copula and degradation tests now constitute a "
    "meaningful robustness check: the B > A > C probabilistic ranking is preserved across all "
    "perturbations, with exceedance probabilities shifting by approximately three percentage points. A "
    "bootstrap analysis (100 resamples of the baseline simulation) confirmed that B overtakes A on "
    "P(ROI>8%) in 100 of 100 resamples, indicating the reranking is a stable structural property "
    "rather than a sampling artifact.", body))


story.append(Paragraph("E. Limitations", h1))
story.append(Paragraph(
    "The parameter distributions are illustrative calibrated assumptions for a reproducible example; "
    "they are not derived from a single proprietary pipeline, and organizations adopting the framework should "
    "substitute pipeline-derived distributions. The demand-volume distribution is a lognormal "
    "calibrated to representative forecast-confidence-interval widths; a production deployment would "
    "fit this distribution to an LSTM (or comparable) demand-forecast model's output. The "
    "timestamp-reconciliation statistics referenced in earlier drafts (0.8-2.4% of records "
    "drift-affected; approximately 80% recoverable) are illustrative ranges drawn from representative "
    "multi-source pipelines, not empirical findings from a specific deployment, and are reported here "
    "as such. The framework is intended as a decision-support mechanism, not a substitute for "
    "organizational capital-governance review.", body))

story.append(Paragraph("V. Discussion", h1))
story.append(Paragraph(
    "The reranking finding has a direct governance implication. The investment with the highest "
    "expected return is not the investment most likely to clear the cost of capital; variance "
    "matters, and variance is determined by which cost components are demand-linked and which are "
    "fixed. An enterprise data team that enforces data contracts at ingestion is, simultaneously, "
    "investing in the reliability of the distributions that feed its own investment decisions [11], "
    "[12], [14]. The framework is a starting point for organizations seeking to align capital allocation "
    "with distributional, rather than point-estimate, risk.", body))
story.append(Paragraph(
    "Implementation Roadmap. Organizations should begin with a pilot covering a single investment "
    "scenario in a single cloud environment before extending to multi-scenario, multi-cloud "
    "deployments. Infrastructure requirements include an orchestration platform (Apache Airflow or "
    "equivalent) with a Python runtime; access to BigQuery, Snowflake, or equivalent warehouse query "
    "logs; and financial-dashboard integration (Power BI, Tableau, or Snowflake-native visualization). "
    "Critical roles include a data-governance owner responsible for contract enforcement at ingestion, "
    "a demand-forecast model owner validating the forecast-distribution calibration, and a finance "
    "stakeholder calibrating the WACC and risk tolerance. Pilot timelines typically span six to eight "
    "weeks from framework design through first scenario evaluation.", body))

story.append(Paragraph("VI. Data and Code Availability", h1))
story.append(Paragraph(
    "The reference implementation (Python, NumPy/SciPy) is available at "
    "https://github.com/adityasumbaraju/aditya_portfolio/tree/main/FinOps-Monte-Carlo-Framework [1]. "
    "The repository includes: main.py (executes the three-scenario simulation and produces Table V); "
    "sensitivity_analysis.py (correlation and data-quality robustness plus bootstrap analysis); "
    "scenarios/scenario_a.py, scenario_b.py, scenario_c.py (scenario ROI equations); "
    "utils/copula.py (Gaussian and Student-t copula sampling); "
    "config/params_config.json (all distributions, correlations, and calibrated parameters); "
    "outputs/roi_statistics.csv and outputs/simulation_results.json (full simulation outputs); and "
    "outputs/sensitivity_analysis.csv (robustness results). The implementation uses representative "
    "parameter values that are illustrative calibrated assumptions for a reproducible example; organizations adopting the "
    "framework should substitute their own pipeline-derived distributions. The public reference "
    "implementation is intended for pedagogical validation of the framework architecture, not for "
    "direct use in capital decisions.", body))

story.append(PageBreak())
story.append(Paragraph("References", h1))
refs = [
    "A. Sumbaraju, \"FinOps Monte Carlo Framework reference implementation,\" GitHub repository. [Online]. Available: https://github.com/adityasumbaraju/aditya_portfolio/tree/main/FinOps-Monte-Carlo-Framework",
    "A. Senova, A. Tobisova, and R. Rozenberg, \"New approaches to project risk assessment utilizing the Monte Carlo method,\" Sustainability, vol. 15, no. 2, 2023, doi: 10.3390/su15021006.",
    "M. Pavlik and G. Michalski, \"Monte Carlo simulations for resolving verifiability paradoxes in forecast risk management and corporate treasury applications,\" Int. J. Financial Stud., vol. 13, no. 2, 2025, doi: 10.3390/ijfs13020049.",
    "K. Douaioui, R. Oucheikh, O. Benmoussa, and C. Mabrouki, \"Machine learning and deep learning models for demand forecasting in supply chain management: A critical review,\" Appl. Syst. Innov., vol. 7, no. 5, 2024, doi: 10.3390/asi7050093.",
    "K. Bandara, C. Bergmeir, and H. Hewamalage, \"LSTM-MSNet: Leveraging forecasts on sets of related time series with multiple seasonal patterns,\" IEEE Trans. Neural Netw. Learning Syst., vol. 32, no. 4, pp. 1586-1599, 2021, doi: 10.1109/TNNLS.2020.2985720.",
    "P. Bhardwaj, \"The role of FinOps in large-scale cloud cost optimization,\" Int. J. Sci. Res. Eng. Manag., vol. 9, no. 1, 2025, doi: 10.55041/ijsrem28086.",
    "D. K. Somajohassula, \"Financial cloud cost optimization: A FinOps framework for modern financial institutions,\" World J. Adv. Res. Rev., 2025, doi: 10.30574/wjarr.2025.26.1.1323.",
    "M. A. Anjum, \"Bridging FinOps practice and machine learning research: A systematic review of cloud cost optimization,\" PeerJ Comput. Sci., vol. 12, 2026, doi: 10.7717/peerj-cs.3964.",
    "S. B. Gosipathala, \"Cloud ETL architecture for streaming analytics: An end-to-end framework,\" Int. J. Sci. Res. Comput. Sci. Eng. Inf. Technol., 2024, doi: 10.32628/cseit24102153.",
    "S. Katiyar, \"Migrating enterprise applications from on-premises to AWS in a multi-cloud environment,\" IJETCSIT, vol. 6, 2025, doi: 10.63282/3050-9246.ijetcsit-v6i4p129.",
    "I. A. Machado, C. Costa, and M. Y. Santos, \"Data mesh: Concepts and principles of a paradigm shift in data architectures,\" Procedia Comput. Sci., vol. 196, 2022, doi: 10.1016/j.procs.2021.12.013.",
    "R. Gopa, \"AI augmented ETL pipelines for automated data quality anomaly detection and governance,\" Int. J. Comput. Exp. Sci. Eng., vol. 11, no. 4, 2025, doi: 10.22399/ijcesen.4124.",
    "E. Kole, K. Koedijk, and M. Verbeek, \"Selecting copulas for risk management,\" J. Financial Econometrics, vol. 5, no. 1, 2007, doi: 10.1093/jjfinec/nbl014.",
    "IBM, \"What is a data contract?,\" IBM Think, 2026. [Online]. Available: https://www.ibm.com/think/topics/data-contract",
]
for i, r in enumerate(refs, 1):
    story.append(Paragraph(f"[{i}] {r}", body))

doc = SimpleDocTemplate(str(OUT), pagesize=letter,
                        leftMargin=0.85*inch, rightMargin=0.85*inch,
                        topMargin=0.8*inch, bottomMargin=0.8*inch)
doc.build(story)
print(f"Built {OUT}")
