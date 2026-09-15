# Agent evaluations

`evals.json` defines report-quality, methodological-boundary, source-integrity, comparison, and underspecified-request / answer-enrichment cases. `trigger_queries.json` records routing expectations and capability limits. `profile-and-pack-cases.json` tests domain-reference selection, conceptual distinctions, and responses to controlled changes. `decision-formation-cases.json` tests alternative formation, epistemic roles, the minimal property contract, correction, Reverse Projection, and proportionality.

Domain expectations identify reference documents and concepts in ordinary language. They do not require stable candidate IDs or an assessment of every concept in a document. A reference can guide coverage but cannot establish a case fact.

In Formation cases, `formation_expected` describes visible or material formation. A false case may retain the internal minimal Tree, provided it stays invisible and does not trigger unnecessary research, interviews, or option expansion.

Run each output eval in a clean context at least three times with the skill and three times without it. `scripts/scaffold_eval_workspace.py WORKSPACE` prepares instructions for these runs; it does not execute a model. Domain, routing, and Formation case suites are separate definitions and need their own run setup when evaluated.

Store outputs, reference selection, tool traces, latency, token usage, and assertion grading outside this repository. Reuse of a baseline and changes to prompts or grading must be disclosed. Unit tests and the evaluation-definition validator do not establish that live agent runs occurred; consult `EVAL_STATUS.md` for the actual scope of evidence.
