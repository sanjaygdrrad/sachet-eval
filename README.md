# Sachet Eval · सचेत

[![CI](https://github.com/sanjaygdrrad/sachet-eval/actions/workflows/ci.yml/badge.svg)](https://github.com/sanjaygdrrad/sachet-eval/actions/workflows/ci.yml)

**An open evaluation harness for AI-generated disaster alerts in Nepal.**

**[→ Try it in your browser](https://sanjaygdrrad.github.io/sachet-eval/)**: paste an official alert and a rewrite (SMS, radio script, translation, AI output) and see what was kept, lost, invented or flipped. It runs entirely in your browser; nothing is uploaded.

Every monsoon, official flood and landslide warnings in Nepal are technical, Nepali-only and slow to reach the people most at risk. Large language models (LLMs) can rewrite them into plain, local-language scripts, and text-to-speech (TTS) can turn those scripts into voice for radio, phone calls and loudspeakers.

But an alert that is easy to understand and **wrong** is worse than no alert. *Sachet* (सचेत, "alert, aware") tests whether AI pipelines can be trusted with that job.

> **Status:** early research tool (v0.5). Factual faithfulness and text-integrity checks work today, tested on a **real DHM flood bulletin** (`cases/real/`) and on clearly-labelled illustrative examples (`cases/examples/`).

## What it checks

| Metric | Question | Status |
|---|---|---|
| **Text integrity** | Is the official text intact before it enters a pipeline? (PDFs in legacy fonts lose conjunct letters) | ✅ v0.2 |
| **Faithfulness** | Does the rewrite keep every critical fact (levels, times, dates, places) and invent none? | ✅ v0.1 |
| **Meaning** | Hazard, status (**above/below** warning or danger level), trend (rising/falling) and action survive, with no flipped meaning | ✅ v0.4 |
| **Channel profiles** | SMS keeps the place, status and action; radio/phone scripts keep everything | ✅ v0.4 |
| **Intelligibility** | Does the spoken audio say what the script says? Measured with speech recognition and word error rate (WER) | 🧩 WER ready; ASR integration next |
| **Comprehension** | Do listeners recall *where, when and what to do*? | 📋 planned (human study) |
| **Channel robustness** | Is it still clear over an 8 kHz phone line, FM radio, a loudspeaker? | 📋 planned |
| **Latency & cost** | Time from bulletin to broadcast-ready audio; cost per minute | 📋 planned |
| **Offline readiness** | Can it run on a laptop or edge device when the internet and power are down? | 📋 planned |

### What counts as "important"
Each rewrite is checked against the official alert for:

| Fact | Example | SMS | Radio / phone script |
|---|---|---|---|
| **What**: the hazard | flood, flash flood, landslide | ✅ | ✅ |
| **Where**: river, station, districts (`must_keep` / `sms_must_keep`) | Narayani, Chitwan | ✅ | ✅ |
| **Status**: above/below warning or danger level | *above the danger level* | ✅ | ✅ |
| **Numbers**: levels, thresholds, times, dates, hotline | 11 m, 8 AM, 1155 | only `sms_keep_numbers` | ✅ |
| **Trend** | rising / falling | – | ✅ |
| **Action** | move to high ground, keep away from the river | ✅ | ✅ |
| **Nothing invented or flipped** | no new numbers; *above* never becomes *below* | ✅ | ✅ |

A rewrite **passes** only if every required item is present and nothing is invented or flipped. Detection is rule-based (Nepali and English keyword lists) so every decision can be read and audited. These definitions are a starting point, to be validated against human judgement and with agencies, broadcasters and listeners.

### Scope: Sachet does not verify that an alert is official
Sachet checks a rewrite **against the text it is given**. Each case records where that text came from, and reports label it **official** (an agency domain or account), **relayed from official** (e.g. via Gati), or **unverified source**. Confirming that an alert is genuine is the job of the issuing agency. Digitally signed CAP alerts would make this verifiable, and would be a valuable step for Nepal's agencies.

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

## Finding: official PDFs can corrupt Nepali text
Text copied from a real DHM flood bulletin (PDF) came out like this:

| Copied from the PDF | Should read |
|---|---|
| `जल ोत` | जल **स्रोत** |
| `मौसम िव ान िवभाग` | मौसम **विज्ञान** विभाग |
| `सतकता तह भदा तलै` | **सतर्कता** तह **भन्दा** तलै |
| `११५५ नंवरको टोल-ि सेवा` | ११५५ नम्बरको **टोल-फ्री** सेवा |

The legacy font encoding drops conjunct letters, so any pipeline that reads the PDF directly hands broken Nepali to the LLM and TTS. `sachet lint` catches it: **14 broken words out of 163 (9%)** in that copy.

```bash
sachet lint cases/real/dhm-flood-bulletin-2078-05-29.raw.txt
```

## Finding: human translations are faithful; SMS summaries drop critical facts
Three real alerts relayed as CAP 1.2 by [Gati](https://github.com/nirajbhusal/gati-alerts) (`cases/real/gati/`): an NDRRMA **danger-level** alert for the Narayani, and DHM **warning-level** alerts for the Lohandra and Roshi rivers. Each contains the official Nepali text, an English translation and 160-character SMS summaries, all written by people.

| Rewrite | Facts kept | Verdict |
|---|---|---|
| English translations (3 alerts) | 12/12 · 9/9 · 7/7 | ✅ 100% faithful |
| 160-character SMS summaries | 45% · 50% · **14%** | ❌ |

The short summaries drop times, warning levels and the 1155 hotline. The Narayani **danger-level** summary keeps only *"the Narayani has crossed the danger level"* and loses **where** (Chitwan, Nawalparasi East/West), **how high** (11 m, peak 13 m) and **what to do**. No rewrite invented a fact. That's the risk to watch for with AI rewrites.

```bash
sachet eval cases/real/gati/
```

## Quick start

Requires Python 3.11+. No other dependencies.

```bash
pip install -e ".[dev]"
sachet eval cases/                       # Markdown report
sachet lint some-bulletin.txt            # check for corrupted Devanagari
sachet from-cap alert.xml --out case.toml   # turn a CAP 1.2 alert into a case
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
may_add   = []          # values a rewrite may add (e.g. an AD date next to a BS date)
source_url = "https://…" # where the official text came from (optional)
issuer = "…"             # optional
issued = "…"             # optional

[[candidates]]
system = "llm-a-simplify-v1"
text = """ ... the rewritten alert ... """
```

## Public portal
`portal/` is a static web page published to GitHub Pages by `.github/workflows/portal.yml`. It loads the **same Sachet Python package** into the browser with [Pyodide](https://pyodide.org) (Python compiled to WebAssembly), so the website and the command line give identical results, and every portal result is covered by the test suite (`tests/test_portal.py`).

- Visitors paste the official alert and the rewrite, choose **SMS** or **radio/phone script**, and optionally list the places that must not be lost.
- Results show **flipped meaning**, **invented**, **missing** and **kept** facts, plus a warning if the official text looks corrupted.
- Wording is deliberate: *"no missing, invented or flipped facts found"*, never *"safe to broadcast"*. The page states that Sachet does not verify whether an alert is official.
- A checked example can be suggested as a new test case through a pre-filled GitHub issue, reviewed before it is added.

Run it locally:

```bash
python scripts/build_portal.py
python -m http.server -d _site 8000     # open http://localhost:8000
```

## Data and credits
- `cases/real/dhm-flood-bulletin-2078-05-29.*`: DHM Flood Forecast Bulletin, republished by DAO Bhojpur (link in the file).
- `cases/real/gati/`: alerts relayed by **Gati (गति)**, [github.com/nirajbhusal/gati-alerts](https://github.com/nirajbhusal/gati-alerts). Gati's translations and summaries are licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Official wording and figures remain the issuing agencies' (DHM, NDRRMA). Changes made for evaluation are noted at the top of each file.

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
