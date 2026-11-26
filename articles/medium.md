<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
<!-- Draft for the owner (M5). Not published. Every number is copied from research/paper/manuscript.md and checked by tests/test_demo_export.py. Publication is the owner's decision (G-PUBLIC). -->

# The mathematics of remembering: a smart review scheduler wins in its own model, and mostly only there

*Draft. By Mohamed Bechir Kefi, independent researcher. A simulation study; not peer-reviewed.*

Flashcard apps decide when you should see a card again. The clever ones keep a model of your memory and show you the cards you are about to forget. That sounds obviously better than reviewing everything on a fixed timetable. But how would you know? If you test the clever scheduler on simulated learners whose memory follows the scheduler's own model, the comparison is rigged in its favour.

MEMORY is a small simulation study that tries to measure how much of the advantage survives when the comparison is made fair. It makes no claim about human learners: every "learner" here is a set of 50 synthetic items following a published forgetting curve.

## The question

Which review schedule maximizes modelled recall under a fixed study budget? Every schedule gets exactly 200 reviews for 50 items, spread over a four-week study window. Recall is measured long after the course: the central test is 281 days after the last study session.

## The method, visually

Each item's recall decays after every review, either exponentially or as a power law, and a successful review slows the decay. Five schedules spend the same budget:

- **uniform**: each item gets four equally spaced reviews (the baseline);
- **expanding**: gaps that double;
- **massed**: every review in the last four days (cramming);
- **Leitner**: the classic box system;
- **greedy**: each day, review the items with the lowest predicted recall.

The interactive page shows these schedules side by side as a calendar: expanding and massed put all 200 reviews on 4 days, the others spread them over every session. The protocol, configurations and seeds were frozen and hashed before any confirmatory run.

## What was measured

**The smart scheduler wins, a little, when it knows the truth.** With exponential forgetting and a scheduler that knows the true model, greedy beat equal spacing by 0.0162 in mean modelled recall (95% interval 0.0110 to 0.0213, 50 paired simulated learners). That is a small effect, and it has a cost: the share of items recalled with probability above 0.9 fell from 0.0200 to 0.

**Give it the wrong model and most of the gain disappears.** On power-law learners, greedy with the right model gained 0.0347; with an exponential model it gained 0.0085 (interval -0.0026 to 0.0195). The frozen rule classifies that as practically equivalent to equal spacing. Exploratory checks show that this label is fragile, but the size of the drop, about three quarters, is not.

**The ranking of schedules is not stable.** Across 72 combinations of forgetting model, budget, retention interval and item difficulty, the ranking found at the central setting changed in 70. Cramming, the worst schedule at the central setting, was the most frequent winner (29 cells), mostly under power-law forgetting, where the time from the last review to the test matters most.

**A negative result about the models themselves.** On public Duolingo data, neither forgetting curve predicted real first-review recall better than a constant guess (log-loss 0.328 for the constant, 0.549 for the best exponential curve, 0.428 for the best power-law curve). So every number above is a property of the assumed model, not of people.

**A check that was not run.** An optional sensitivity check of the power-law time scale had no frozen configuration and was not run. Robustness to that parameter is untested.

## What this does and does not show

It shows that, inside these models, the answer to "which schedule is best" depends on the forgetting model, the budget, the retention interval and what the scheduler knows. It shows how evaluating a model-based scheduler on learners built from its own model can overstate its advantage. It does not show that any schedule improves human learning, and it says nothing about any commercial product.

## Limitations

Recall is a model probability, not a measurement of people. The scheduler is given each item's true initial difficulty, which no real app has. Cramming and expanding review concentrate 50 reviews on a single day, a load the other schedules never reach. Two update parameters and the power-law time scale are planning values, not estimates.

## Reproduce it

Code, frozen protocols, results, the manuscript and the experiment reports: https://github.com/mohamedbechirkefi/memory-spaced-repetition. Interactive page: https://memory-spaced-repetition.kefimohamedbechir.workers.dev. The manuscript is `research/paper/manuscript.md`; the reports are `research/experiments/EXP-00N/report.md`.

*An AI system (Claude, Anthropic) was used as a research and development assistant for code, analysis scripts and documentation under the author's direction; it is not an author.*
