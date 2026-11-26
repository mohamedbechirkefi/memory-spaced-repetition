<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
<!-- Draft for the owner (M5). Not published. Numbers copied from research/paper/manuscript.md and checked by tests/test_demo_export.py. Publication is the owner's decision (G-PUBLIC). -->

# LinkedIn draft

Does a "smart" spaced-repetition scheduler beat a fixed timetable? Only, it seems, when it is tested on its own model.

I built MEMORY, a small simulation study with frozen protocols: five review schedules, the same budget of 200 reviews for 50 synthetic items, two published forgetting models, 18,550 simulated runs, with protocols, configurations and seeds hashed before any confirmatory result.

One defensible finding: a scheduler that knows the true memory model beat equal spacing by 0.0162 in mean modelled recall (95% interval 0.0110 to 0.0213). Given the wrong model, its gain on power-law learners fell from 0.0347 to 0.0085, which the frozen rule classifies as equivalent to equal spacing.

Caveat: these are simulated learners, not people. Neither forgetting model predicts real first-review recall from public Duolingo data better than a constant, so this says nothing about human learning gains. One planned sensitivity check was not run.

Manuscript (preprint draft, not peer-reviewed), reports and code: https://github.com/mohamedbechirkefi/memory-spaced-repetition
Interactive page: https://memory-spaced-repetition.kefimohamedbechir.workers.dev

Mohamed Bechir Kefi, independent researcher. An AI system (Claude, Anthropic) was used as a research and development assistant.
