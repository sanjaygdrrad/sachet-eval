# Sachet Eval · सचेत

[![CI](https://github.com/sanjaygdrrad/sachet-eval/actions/workflows/ci.yml/badge.svg)](https://github.com/sanjaygdrrad/sachet-eval/actions/workflows/ci.yml)

**An open evaluation harness for AI-generated disaster alerts in Nepal.**

Every monsoon, official flood and landslide warnings in Nepal are technical, Nepali-only and slow to reach the people most at risk. Large language models (LLMs) can rewrite them into plain, local-language scripts, and text-to-speech (TTS) can turn those scripts into voice for radio, phone calls and loudspeakers.

But an alert that is easy to understand and **wrong** is worse than no alert. *Sachet* (सचेत, "alert, aware") tests whether AI pipelines can be trusted with that job.

> **Status:** early research tool (v0.1). Phase 1, factual faithfulness, works today. The example cases are **illustrative**, not official bulletins.

## What it checks

| Metric | Question | Status |
|---|---|---|
| **Faithfulness** | Does the rewrite keep every critical fact (levels, times, dates, places) and invent none? | ✅ v0.1 |
| **Intelligibility** | Does the spoken audio say what the script says? Measured with speech recognition and word error rate (WER) | 🧩 WER ready; ASR integration next |
| **Comprehension** | Do listeners recall *where, when and what to do*? | 📋 planned (human study) |
| **Channel robustness** | Is it still clear over an 8 kHz phone line, FM radio, a loudspeaker? | 📋 planned |
| **Latency & cost** | Time from bulletin to broadcast-ready audio; cost per minute | 📋 planned |
| **Offline readiness** | Can it run on a laptop or edge device when the internet and power are down? | 📋 planned |

### Faithfulness (v0.1)
- Extracts **dates, times and numbers** from the official alert and the rewrite. **Devanagari and Latin digits are treated as equal** (`६.८` = `6.8`), and Nepali number grouping (`1,00,000`) is understood.
- Checks that named places, rivers and highways (`must_keep`) survive, accepting any listed spelling (`नारायणी` / `Narayani`).
- Flags anything **missing** and anything **invented**. The verdict is strict: an output passes only if nothing is missing *and* nothing is invented.
- Context numbers can be marked `may_drop`: they may be left out, but never changed.

Example output (from the illustrative cases in `cases/examples/`):

| Case | System | Facts kept | Missing | Invented | Verdict |
|---|---|---|---|---|---|
| `flood-ne-01` | example-faithful | 5/5 (100%) | – | – | ✅ pass |
| `flood-ne-01` | example-unsafe | 1/5 (20%) | 6.5, 6.8, 7:00, देवघाट | 8.6, 9:00 | ❌ fail |

## Quick start

Requires Python 3.11+. No other dependencies.

```bash
pip install -e ".[dev]"
sachet eval cases/                       # Markdown report
sachet eval cases/ --json --out r.json   # machine-readable
sachet eval cases/ --strict              # exit code 1 if anything fails (for CI)
pytest                                   # the evaluator's own tests
```

## Writing a case

One TOML file per alert: the official text, the names that must survive, and the outputs of each system under test.

```toml
id = "flood-ne-01"
language = "ne"
source = """
बाढी चेतावनी: नारायणी नदीको देवघाट मापन केन्द्रमा पानीको सतह ६.८ मिटर पुगेको छ ...
"""
must_keep = [["नारायणी", "Narayani"], ["देवघाट", "Devghat"]]
may_drop  = []          # context numbers that may be omitted

[[candidates]]
system = "llm-a-simplify-v1"
text = """ ... the rewritten alert ... """
```

## Principles
- **Public data only.** Cases use public bulletins or clearly-labelled illustrative examples; no personal data.
- **Assistive, not autonomous.** Sachet supports a human-in-the-loop workflow. It is not a replacement for official warning channels.
- **Transparent first.** Rule-based checks anyone can read and audit, before any model-based scoring.

## Roadmap
See [docs/PLAN.md](docs/PLAN.md).

## Citation
If you use Sachet Eval in research, please cite it (see [`CITATION.cff`](CITATION.cff)).

---
Built by [Sanzay Bhandari](https://sanzay.com.np) · MIT licence
