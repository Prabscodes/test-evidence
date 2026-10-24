"""Narrow fail-closed contradiction signal, not a semantic correctness judge.

Only explicit wording in the model's own rationale is inspected. This guard may
abstain unnecessarily and does not detect all missing-authority explanations.
"""
import re
_AUTHORITY=r'(?:requirement|specification|contract)'
_PATTERNS=[
    rf'\b{_AUTHORITY}\s+(?:does|do)\s+not\s+(?:specify|define|state|clarify)\b',
    rf'\b{_AUTHORITY}\s+(?:is|remains)\s+(?:unspecified|undefined|ambiguous|unclear|silent)\b',
    rf'\b{_AUTHORITY}\s+leaves\s+[^.!?\n]{{1,100}}\b(?:unspecified|undefined|ambiguous|unclear)\b',
    r'\b(?:policy|expected behavior|expected outcome)\s+(?:is|remains)\s+(?:unspecified|undefined|ambiguous|unclear)\b',
]

def acknowledges_missing_authority(rationale):
    return any(re.search(pattern,rationale,re.I) for pattern in _PATTERNS)
