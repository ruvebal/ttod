# Innova EDU UDIT 2026-27 — ATELIER-IA submission pack

**Call:** Convocatoria competitiva de proyectos internos de innovación educativa UDIT 2026-2027 (V2, 20/10/2026).
**First cut closes:** **30 November 2026** (inclusive). Second cut: 31 January 2027, only if money remains.
**Send to:** `otc@udit.es` · subject **`INNOVA EDU UDIT 2026-2027 – ATELIER-IA – Vega Balbás`**.
**Programme context:** [`../STRAND-B-PROGRAMME.md`](../STRAND-B-PROGRAMME.md) (case 3 of Strand B).

## Package (§9.2)

| # | Document | Source | State |
| --- | --- | --- | --- |
| 1 | Memoria técnica PDF (≤ 15 p. without cover, references, letters) | [`MEMORIA-TECNICA-ATELIER-IA-ES.md`](MEMORIA-TECNICA-ATELIER-IA-ES.md) → `make` here | Draft; `[PENDIENTE]` markers to fill |
| 2 | Short CV of the IP (≤ 4 p.) | owner | To do |
| 3 | Commitment letter from the pilot entity | not needed: the pilot is the IP's own UDIT group | n/a |
| 4 | Declaraciones responsables: other funding, conflicts of interest, ethics, data protection, AI use, truthfulness, third-party licences (§13.3) | [`DECLARACIONES-RESPONSABLES-ES.md`](DECLARACIONES-RESPONSABLES-ES.md) | Draft; to sign |

Separate from the call (do not attach): [`SOLICITUD-RECURSOS-DEPARTAMENTO-ES.md`](SOLICITUD-RECURSOS-DEPARTAMENTO-ES.md)
asks the department for deployment, communication and congress support.

## Rubric self-check (§10) — where each criterion is answered

| Criterion | Pts | Memoria § | Weak spot to strengthen before sending |
| --- | ---: | --- | --- |
| 1 Necesidad y calidad educativa (min 50 %) | 25 | 1, 2 | Confirm n and the semester-2 React product |
| 2 Grado de innovación | 15 | 3 | — |
| 3 Pilotaje y evaluación (min 50 %) | 20 | 4, 7 | Name the pre/post questionnaire once the literature search is done; I1 baseline is computed in M1 |
| 4 Viabilidad y presupuesto | 15 | 7.3, 8, 9 | Team is IP-only: name a custodian and a second rater if possible |
| 5 Alineación estratégica | 10 | 11 | No TFG linked yet (the extra points go to TFG/TFM links) |
| 6 Inclusión, ética, accesibilidad, ODS | 10 | 6.2–6.4, 11 | — |
| 7 Transferencia y escalabilidad | 5 | 10 | — |

## Constraints that shaped the design

- **No intervention or data collection before resolution** (§7) → case 3 is FE I semester 2 (Feb–Jun 2027); cases 1–2 appear only as prior results and teaching observations, not research data.
- **New instruments (questionnaires, pre/post task) → back to the ethics committee** before recruitment (§13.1; no retrospective review).
- **AI never grades** (§13.2, Reglamento (UE) 2024/1689) → both rubrics are human-applied.
- **Third-party licences must not restrict UDIT's use and continuity** (§13.3) → the local model is swappable; Redis 7.4+ (RSAL/SSPL) to be replaced by Valkey (BSD-3).

## Build

```bash
make -C docs/research/innova-edu-2026-27      # → MEMORIA-TECNICA-ATELIER-IA-ES.pdf
```
