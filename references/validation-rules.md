# Validation Rules

Validation finds structural errors and review signals; it does not prove methodological correctness.

## Schema and semantics

Check required keys, field types, date formats, language-neutral enums, criterion-specific judgment codes, unique IDs, active contrast, and every reference target. Accept valid Schema 3.0 records; require `profile_id`, `adaptation.domain_pack_ids`, and `adaptation.domain_pack_use_case` for Schema 3.1. The use case must be selected from the chosen pack's included use cases, or be `null` when no pack is selected.

## Evidence

Check claim-source relations, explicit criterion evidence bases, contrast and outcome references, certainty calculations, artifact capabilities, and source support status.

## Artifact safety

Local artifacts must remain under the skill root, may not escape through symbolic links, must use allowed extensions, and must remain below the size limit. Remote URLs cannot be marked locally integrity-verified without a snapshot.

## Governance

Check generated versus imported lifecycle, mandatory human review for formal drafts, supported formal scope, evidence assessment, EtD precheck, methodological reviewer type, and authorization authority.

## Profiles and packs

Check registry source references, inheritance, cycles, include/exclude conflicts, criterion mappings, profile presence, profile-to-method alignment, pack identity, pack scope, version, SHA-256, source basis, and single-pack selection for Schema 3.1.

Legacy Schema 3.0 Packs without a scoped use case and complete current-candidate
assessment cannot be carried unchanged into Schema 3.1. Keep the record on 3.0,
detach the legacy selection, or perform a fresh current-Pack assessment.

## Exit codes

- `0`: no errors; warnings may remain;
- `1`: one or more validation errors;
- `2`: parsing or execution failure.
