# Adaptation Rules

## Purpose

Adapt selected Reference Profile criteria to a case without creating domain-specific pipelines or implying external endorsement.

## Case derivation

Derive and justify the owner, mandate, perspective, jurisdiction, population, options, active contrast, outcome roles and importance, evidence designs, equity subgroups, baseline risk, thresholds, constraints, information gaps, implementation, and monitoring.

## Reference Profile selection

Choose the profile by question family, perspective, and conclusion form. Use an official `grade.*` profile only when those facts fit a health question. Use `generic.etd` otherwise. Do not guess an official profile.

## Decision Formation boundary

When Decision Formation is active, keep curated preset references and case-specific research separate:

- a Domain Pack or other preset reference model critiques coverage, suggests candidate criteria or option families, and reduces omission or arbitrary framing;
- query-time Research establishes case-specific facts, constraints, existing patterns, and technical possibilities.

Neither is automatically authoritative over the other. A pack is not case evidence, and case-specific findings do not silently rewrite the pack. When they diverge, use the difference to revise Formation Context or add, revise, merge, or remove a material Question according to the claim type.

Do not compose multiple Domain Packs merely to expand the option space. The existing one-pack rule for Schema 3.1 remains unchanged. Cross-domain needs discovered during Formation remain case context or unresolved gaps unless a later version defines a stable composition rule.

## Domain Pack candidate selection

Each Domain Pack contains stable candidate IDs. For each material candidate record selection, reason, case evidence, and resulting record paths.

Do not adopt all pack candidates automatically. Absence of selection is not evidence of irrelevance; record a reason when a plausible high-impact candidate is excluded.

For new Schema 3.1 records, select at most one pack. Preserve the pack version, SHA-256, source basis, candidate source references, and normative status. A pack candidate may map to a standard criterion or an `additional_criteria` path.

## Cross-domain needs

Do not compose packs in Schema 3.1. Record the unrepresented need and conflict in the case and `design-gap-log.yaml` when recurrent. Legacy Schema 3.0 records that already compose packs remain valid and must preserve provenance and separate health from non-health certainty methods.

## Contrast discipline

A Canonical Record has one active contrast. For A, B, C, and current practice, create the required pairwise or policy-relevant contrast records and synthesize them transparently. Narrative support may compare several options directly.
