# Sachet Eval: plan

## Research context
A comparative analysis of **LLM-enhanced text-to-speech pipelines for multilingual disaster communication in Nepal**:

```
Official bulletin → LLM (simplify · translate · localise) → TTS (voice) → channel (radio · IVR phone · loudspeaker)
```

Sachet Eval is the open measurement layer: it scores each stage, so different LLMs, TTS systems and prompts can be compared on safety-relevant criteria, not just on how natural they sound.

## Phases

### Phase 1: faithfulness and text integrity ✅ (v0.2)
- [x] Normalisation for Nepali (Devanagari digits, number grouping, zero-width joiners)
- [x] Extraction of dates, times and numbers
- [x] `must_keep` name groups with spelling aliases; `may_drop` context numbers
- [x] Strict pass/fail verdict; Markdown and JSON reports; CLI; CI
- [ ] Nepali number **words** (e.g. तीन → 3) and Bikram Sambat month names
- [ ] Units-aware comparison (6.8 m vs 680 cm)
- [x] First real case: DHM Flood Forecast Bulletin, 2078-05-29 (`cases/real/`), with source link and metadata
- [x] `sachet lint`: detects Devanagari corrupted by legacy-font PDF extraction (finding: 9% broken words in the copied bulletin)
- [x] CAP 1.2 importer (`sachet from-cap`): works with any standard public-alert feed
- [x] Real cases from Gati (CAP 1.2): NDRRMA Narayani **danger-level** alert; DHM Lohandra and Roshi warning-level alerts
- [x] `may_add` for legitimate additions (e.g. AD dates in English translations)
- [x] **Meaning checks**: hazard, status above/below warning or danger level, trend, action; flipped meanings flagged
- [x] **Channel profiles**: SMS (place · status · action, numbers optional) vs. full radio/IVR script
- [x] **Provenance labels**: official · relayed from official · unverified source
- [ ] Validate "important" with human annotators (agreement score) and with DHM/NDRRMA, community radio and listeners

### Public portal (next)
- [ ] GitHub Pages site: paste official alert + rewrite, pick SMS or radio script, see the checklist
- [ ] Runs in the browser via Pyodide (same tested Python code); nothing is uploaded or stored
- [ ] Clear wording: "no missing or invented facts found", never "safe to broadcast"; not a verifier of official status
- [ ] Optional: turn a checked example into a pre-filled GitHub issue to contribute a test case
- [ ] More real cases: an NDRRMA heavy-rain advisory, a landslide or road-closure notice
- [ ] Unicode conversion of legacy-font (Preeti-style) PDF text, and measuring how much it recovers

### Phase 2: intelligibility
- [x] Word error rate for Devanagari and Latin scripts
- [ ] Speech-recognition back-check: TTS audio → transcript → WER against the script
- [ ] Faithfulness re-run on the *transcript* (did the spoken numbers survive?)

### Phase 3: channels, latency, offline
- [ ] Simulated channels: 8 kHz telephone band, FM-style compression, outdoor noise
- [ ] Timing and cost per minute of audio for each pipeline
- [ ] Offline profile: CPU-only runs on a laptop / edge device

### Phase 4: people
- [ ] Listening tests (naturalness, MOS) and comprehension checks with native speakers
- [ ] Languages beyond Nepali (to be decided with the research scope)

## Open decisions
1. Languages in scope beyond Nepali.
2. Shortlist of LLMs and TTS systems to compare.
3. Source and licence of public bulletin samples.
4. Whether results are published as a public leaderboard.
