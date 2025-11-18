## Goal
Align document verification and the user-facing "AI Analysis Report" UI to always use data from the latest Full Application (student + parents), and display identity match context clearly.

## Backend Changes
1. Route specialized services using Full Application:
- In `ai_document_analysis`, fetch latest `FullApplication` for `request.user` and build `user_application_data` including `first_name`, `middle_name`, `last_name`, `barangay`, `house_no`, `street`, `district`, `mother_name`, `father_name`.
- Pass `user_application_data` to specialized verifiers:
  - Voter Certificate → `verify_voter_certificate_document(..., user_application_data=...)`
  - Birth Certificate → `verify_birth_certificate_document(..., user_application_data=...)`

2. Identity fallback in voter verification:
- If voter name does not match student, check `mother_name` and `father_name`.
- Set `identity_verified` (true/false) and `identity_type` (`student`/`mother`/`father`/`none`).
- Validity requires: required elements + confidence ≥ 0.70 + identity_verified.

3. Persist normalized AI fields:
- Write `ai_confidence_score` (0–1), `ai_analysis_completed`, `ai_auto_approved`, concise `ai_analysis_notes`.
- Save `ai_key_information` including `algorithms_results` and identity fields (`identity_verified`, `identity_type`, `parent_matches`).

4. Admin AI details endpoint:
- Ensure `ai_details` includes the new identity fields from `ai_key_information` so admins can view which identity source matched.

## Frontend Changes
1. DocumentRequirements modal (student):
- When opening Details, display:
  - AI Decision: `Auto-Approved` vs `Manual Review Required` using `ai_auto_approved`.
  - Identity Source: show `Verified against: Student` or `Mother` or `Father` if available in `ai_key_information`.
  - Confidence bar and label (High/Medium/Low) from `ai_confidence_score`.
  - Analysis notes and recommendations lists.
- If identity fields are missing from `ai_key_information`, fetch latest `/full-application/` and display student/parent names in the context panel.

2. Optional convenience:
- Cache Full Application data in a shared context so Documents page can render identity context without refetching.

## Testing & Verification
1. Unit/integration:
- Submit Voter Certificate with voter name matching student → verified.
- Submit Voter Certificate matching mother/father → verified with identity_type `mother`/`father`.
- Submit with mismatched student and parents → invalid due to identity.

2. Manual checks:
- Trigger `POST /api/ai-document-analysis/` for affected docs; confirm DB updates:
  - `ai_confidence_score > 0`
  - `ai_auto_approved` reflects identity and confidence
  - `ai_key_information.identity_verified` and `identity_type` present.
- Open Details modal; verify identity source and decision badge are shown.

## Rollout
- Backend first; then frontend UI enhancements.
- Reprocess recent voter and birth documents via admin reanalyze to populate identity fields.

Confirm to proceed with implementing these changes end-to-end.