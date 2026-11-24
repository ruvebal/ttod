<!--
Grounding ledger — ATELIER-IA memoria + Strand B programme. INTERNAL (never attach to the submission).
Pass run 2026-11-24 by Claude (Anthropic) under the studio rule: discover in vectors, cite from Ahmes nodes.
-->

# Grounding ledger: ATELIER-IA (2026-11-24 pass)

## What was run

| Layer | Tool | Scope | Result |
| --- | --- | --- | --- |
| Discover (neural set) | `grounding-graph/scripts/cross_project_neural_search.py` → DevIAC `:8100/vectors/search` | 20 queries over every project's embeddings (AI × education × real projects × GitHub × curriculum × ethics × accessibility) | ~70 candidate vaults; ~30 on-topic |
| Discover (pointer index) | `athanor search` | `profield-frontend-pedagogy`, `ai-regulation` (svcm), `profield-stem-code-ai-epistemology-critique`, `mondrian-project`; 11 claim-targeted queries | node + page pointers |
| Cite gate | `ahmes query --cite <db>:<node> --style chicago-author-date --require-evaluator-safe` | 60 Athanor pointers + 36 DevIAC-only sources (node picked by full-text match: `--semantic` needs sqlite-vec, not installed) | evaluator_safe = yes / no recorded below |

Vector and Athanor hits are **discovery only**. Only rows marked **SAFE** ground a sentence in the memoria with a page.

## Citations now in the memoria

| Memoria cite | Claim it carries | Vault (hash) · node · page | Gate |
| --- | --- | --- | --- |
| Alpizar-Chacon & Keuning 2025, 1 | Advanced web dev students use GenAI for code and ideas, report more learning and productivity, fear over-reliance and wrong solutions | `133cc5e4` · `d96e3655` · p1 | SAFE |
| Alpizar-Chacon & Keuning 2025, 3 | Precedent: 14 students, signed consent for AI-related assignments, anonymised quotes, voluntary, withdrawal | `133cc5e4` · `bccb6ab6` · p3 | SAFE |
| Isa et al. 2026, 1 | Most studies rely on self-report or short isolated tasks; this one analyses 448 chat logs from 147 students in a senior web course with realistic assignments | `eabb6c18` · `65f15dc1` · p1 | SAFE |
| Zhu & Liu 2026, 2 | GenAI improves assignment quality; unverified submissions persist; no improvement in proctored no-LLM exams | `531d545d` · `27d14ce7` · p2 | SAFE |
| Liu, Fan & Pan 2026, 1 | Attenuated metacognitive calibration: perceived readiness vs independent capability | `dc2bd27d` · `a3364b94` · p1 | SAFE |
| Davalos & Zhang 2026, 8 | Revision traces show effort, reasoning and possible AI involvement beyond the final product | `7e38e20f` · `25ddf859` · p8 | SAFE |
| Phung et al. 2025, 9 | Planning hints associated with higher performance; causality not established | `ea8cf54c` · `b4a6268a` · p9 | SAFE (but RIS author order and year are wrong; see B11) |
| Nikolić & Basta Nikolić 2026, 1 | Four pillars (process, oral defence, authentic task, AI policy); paper reports no empirical or validation data | `5a9bceda` · `8b8e7378` · p1 | SAFE |
| Park 2025, 2, 11 | GenAI disrupts dialogic critique and diffuses ethical responsibility in studio education; calls for assessment that values reflection and process transparency | `b023e745` · `edc5c5f0` p2, `2c2b4a48` p11 | SAFE |
| Mak et al. 2025, 1 | Ethical/societal impacts of GenAI in higher computing education: equity, integrity, bias, data provenance | `673a2306` · `b82dd0dc` · p1 | SAFE |
| Wohlin et al. 2012, 33 | A case study is observational with less control than an experiment | `764e4900` · `7a305cf3` · p33 | SAFE |
| Shihab 2025 · López-Pernas 2025 · Garcia 2025 | (already cited) | `29f3d2f5` · `205390e7` · `8fef58f2` | SAFE |

## Enrichment list: what you can fix or fetch

### A. Cited in the memoria, DOI-real, but **no Ahmes vault** (acquire the PDF and ingest)

| # | Reference | DOI |
| --- | --- | --- |
| A1 | Prather et al. 2024, "The Widening Gap" (ICER) | 10.1145/3632620.3671116 |
| A2 | Brown & Guzdial 2024, "Confidence vs Insight" (SIGCSE TS) | 10.1145/3626252.3630813 |
| A3 | McGill et al. 2023, "Conducting Sound, Equity-Enabling CER" (ITiCSE WGR) | 10.1145/3623762.3633495 |
| A4 | Fischer et al. 2024, trustee-based consent for process data (ICER) | 10.1145/3632620.3671125 |
| A5 | Runeson, Höst, Rainer & Regnell 2012, *Case Study Research in SE* (Wiley) | 10.1002/9781118181034 |
| A6 | ITiCSE 2026 WG report on post-introductory GenAI (title and authors still unknown in the memoria) | 10.1145/3760545.3783970 |

### B. In Ahmes but **failing the gate** (metadata repair: RIS author/year/DOI)

| # | Source | Vault hash | Problem |
| --- | --- | --- | --- |
| B7 | *Computer Science Curricula 2023* | `da20f30d` (two vaults) | author from slug, conf 0.60 |
| B8 | Heckman et al. 2022 (TOCE) | `12dd71c4` | slug author; RIS DOI is a placeholder `10.1145/nnnnnnn` |
| B9 | Runeson & Höst 2009 (EMSE) | `30849aa9` | conf 0.70; year 2008 (online) vs 2009 (issue) |
| B10 | Regulation (EU) 2024/1689 (AI Act); Annex III(3)(b) "evaluate learning outcomes" at p127 | `bba63044` | slug author; needs corporate author |
| B11 | Phung et al. 2025, *Plan More, Debug Less* (AIED 2025) | `ea8cf54c` | passes, but RIS lists Brooks first and has no year or DOI |
| B12 | **Nelson & Ponciano 2021**, GitHub Classroom for project-based courses | `f1031131` | BIBLIO-GAP. Would ground the GitHub claim |
| B13 | **Kazemitabaar et al. 2024**, CodeAid classroom deployment (CHI) | `23259ff1` | filename used as author |
| B14 | **Vega, Jiménez & Villalobos**, Cupi2 incremental PBL for CS1/CS2 | `3a9560e8` | BIBLIO-GAP. Would ground the walking skeleton / incremental product |
| B15 | **RIED (2082-1054)**, "Generative AI and transformation of teaching in higher education: systematic review and conceptual model" | `969e7999` | BIBLIO-GAP. Top vector hit (17×); Spanish-language |
| B16 | **Díaz et al.**, *Beyond Detection*, GenAI assessment and governance at UPM (arXiv 2607.01255) | `569c5da4` | slug author. Spanish university governance, ideal for UDIT |
| B17 | Valverde García et al. 2025, web accessibility on Spanish university websites (Edutec) | `6c26bafb` | conf 0.70 |
| B18 | "I Would Have Written My Code Differently" (10.1145/3696630.3731663) | `415dcd25` | slug author. Fits RQ-C2 |
| B19 | Ma, Xie & Li, design implications for AI programming tools (arXiv 2603.22673) | `c966127a` | BIBLIO-GAP |
| B20 | *Scaffolding Metacognition in Programming Education* (arXiv 2511.04144) | `9eaf7220` | BIBLIO-GAP |
| B21 | Tsai, Shih & Hsieh, design-based learning for web design skills (10.1186/s41239-021-00308-4) | `2270c733` | BIBLIO-GAP |
| B22 | *Beyond the Hype* GenAI CER review (arXiv 2412.14732) | `42c07600` | BIBLIO-GAP |
| B23 | Peffers et al. 2007, design science research methodology (JMIS) | `e5250c74` | BIBLIO-GAP |
| B24 | **Noll 1966**, "Human or Machine", Mondrian vs computer picture (*Psychological Record*). For the Neoplastix case | `adfa5020` | BIBLIO-GAP |
| B25 | Fleischmann 2026, GenAI in design education (10.1007/s10798-025-10045-8) | `7f94e167` | BIBLIO-GAP |

Bold rows would strengthen the memoria most once they pass.

### C. Topics with **no source in the studio corpus** (the vector search returned off-topic hits)

Suggested search targets. These are not verified here; look them up and check before citing:

- **Communities of practice / legitimate peripheral participation** (Lave & Wenger, *Situated Learning*, 1991): theory for "cohort as a team of developers".
- **Peer code review in higher education** (e.g., a systematic review of peer code review in computing education).
- **Studio-based learning in computing** (e.g., Hundhausen and colleagues on studio-based instructional models).
- **GitHub in software engineering courses** beyond Nelson & Ponciano (e.g., student experiences with GitHub in SE courses).
- **Design-based research in education** (Design-Based Research Collective 2003; Barab & Squire 2004). The corpus has design *science* (Peffers), not DBR.
- **Validated instruments for the pre/post questionnaire.** This blocks §7.2: a programming self-efficacy scale and an AI-literacy scale.
- **Code explanation tasks** ("explain in plain English" lineage) as the basis of the explain-and-modify task.
- **Oral examinations / vivas** to verify authorship in computing.
- **Experiential learning** (Dewey; Kolb). The corpus returns Bybee's 5E model, not these.
