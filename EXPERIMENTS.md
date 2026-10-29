# Experiments

Run: `uv run python -m evals.run <name>` → results in `evals/results/`.

## 2026-10-29 · baseline (5 runs)

Same setup, repeated 5× to measure noise.

**Scores:** 14, 14, 14, 12, 13 → **median 14/20 (70%)**, range 12–14.

**Always failed (5/5):** same 6 cases as the first baseline.

**Flaky:**
- `lockbits-count-48pa-vs-328p` (failed 2/5): model sometimes says 6 lock bits for the 48PA
- `reset-random-low-battery` (failed 1/5): **false negative**, answer said "brownout", `must_contain` expects "Brown-out"

**Takeaway:** baseline to beat is **14/20**; a ±2 swing is noise.
