# Feedback on Week 06 runs — Floyd

Good work getting all 12 runs done with the real `track_id` join. Your numbers
are recorded in `results/week06/README.md`. A few things to fix and two bigger
ideas to understand.

## Please fix in your logs (record-keeping)

- **Save as `.md`, not `.docx`.** Copy `docs/STUDENT_RUN_LOG_TEMPLATE.md` and edit
  it as plain text. Word files can't be diffed or reviewed in git, and they leave
  lock files behind (`~$...docx`). I've already converted your 12 into `.md`.
- **Settings vs command must match.** On S14, S15, S16 clean, your Settings say
  `z-threshold: 0.5` but the command says `--z-threshold 1.0`. Your results match
  0.5, so the command text is wrong. When they disagree we can't tell what
  actually produced the result — always paste the real command.
- **Epsilon is always 0.5.** You listed epsilon `1.0` (S17 clean) and `2.0` (S16,
  S17 poisoned). That's the *z-threshold*, not epsilon. Every file this term is
  `eps0.5`. Read it straight off the filename.
- **Typo:** `co2` should be `c02` in the "cameras targeted" field (cosmetic, your
  commands were correct).

## Two things worth understanding (not your fault)

1. **The poison is on c01 AND c02 — that's 2 of 3 cameras.** The detector assumes
   *most* cameras are clean and flags the odd one out. When the majority is
   poisoned, that logic inverts and it flags the one **clean** camera (c03) — which
   is exactly what you saw on S11 and S15. So a low score here is the *expected*
   behavior of this attack setup, not the detector being broken. The real test is
   poisoning only **one** camera (coming up — the single-camera sweep).

2. **Answering your z-score questions.** A higher z just means "further from the
   other cameras," not "more anomalies," and a negative z just means "closer than
   average" (not bad). With only 3 cameras the math is shaky: you'll keep seeing
   the same `0.674491` / `-0.674491` / `0` values, and once in a while a huge one
   (your 53, 22, and 314). Those giant numbers come from the variance channel and
   aren't meaningful — they're an artifact of having just 3 data points. Good
   catch noticing they looked wrong.

## Nice observations you already made

- Noticing the recurring `0.674491` and the implausibly large z-scores — that's
  the n=3 degeneracy above.
- Spotting that the clean camera got flagged on poisoned runs — that's the
  majority-poison inversion. You were reading the results correctly.
